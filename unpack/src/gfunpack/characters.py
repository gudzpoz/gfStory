import logging
import os
import pathlib
import re
import subprocess
import threading
import typing

import tqdm
import UnityPy
from UnityPy.classes import Sprite, Texture2D
from UnityPy.files import ObjectReader

from gfunpack import utils

_logger = logging.getLogger('gfunpack.character')
_warning = _logger.warning

_character_file_regex = re.compile('^.+character(.*)\\.ab$')
_character_container_regex = re.compile('^assets/characters/([^/]+)/pic(?:_he)?/([^/]+)\\.png$')
_character_npc_regex = re.compile('^assets/characters/([^/]+)/([^/]+)\\.png$')
_character_fairy_regex = re.compile('^assets/resources/dabao/pics/(fairy)/([^/]+)\\.png')
_variation_name_regex = re.compile('_\\d+$')


def _get_pic_of_type(pics: list[Sprite | Texture2D], t: typing.Literal['Sprite'] | typing.Literal['Texture2D']) -> (Sprite | Texture2D):
    filtered = [pic for pic in pics if pic.type.name == t]
    assert len(filtered) == 1
    return filtered[0]


def _get_sprite_path_id(pics: list[Sprite | Texture2D]) -> int:
    return typing.cast(Sprite, _get_pic_of_type(pics, 'Sprite')).path_id


def _get_texture(pics: list[Sprite | Texture2D]) -> Texture2D:
    return typing.cast(Texture2D, _get_pic_of_type(pics, 'Texture2D'))


_special_characters = [
    '/tank_',
    '_tank/',
    '/org_griffin/',
    '/org_commander/',
]

_special_files = [
    '561type',
    'welrod2103',
    'dupijin',
]


class CharacterCollection:
    directory: pathlib.Path

    destination: pathlib.Path

    resource_files: list[pathlib.Path]

    path_id_index: dict[int, pathlib.Path]

    invalid_path_id_index: dict[int, tuple[pathlib.Path, str]]

    all_path_id_index: dict[int, pathlib.Path]

    character_index: dict[str, list[pathlib.Path]]

    hd: bool

    pngquant: bool

    force: bool

    concurrency: int

    _semaphore: threading.Semaphore

    def __init__(self, directory: str, destination: str,
                 hd: bool = False, pngquant: bool = False, force: bool = False, concurrency = 8) -> None:
        self.directory = utils.check_directory(directory)
        self.destination = utils.check_directory(destination, create=True)
        self.path_id_index = {}
        self.invalid_path_id_index = {}
        self.all_path_id_index = {}
        self.character_index = {}
        self.hd = hd
        self.pngquant = utils.test_pngquant(pngquant)
        self.force = force
        self.concurrency = concurrency
        self._semaphore = threading.Semaphore(concurrency)
        self.resource_files = []
        self.resource_files.extend(self.directory.glob('*resourcefairy.ab'))
        self.resource_files.extend(path for path in self.directory.glob('*character*.ab') if 'spine' not in str(path))
        self._test_commands()
        self.load_files()

    def _test_commands(self) -> None:
        try:
            subprocess.run(['magick', '--help'], stdout=subprocess.DEVNULL).check_returncode()
            subprocess.run(['convert', '-version'], stdout=subprocess.DEVNULL).check_returncode()
        except FileNotFoundError as e:
            raise FileNotFoundError('imagemagick is required to merge alpha layers', e)

    @classmethod
    def _try_alpha_names(cls, name: str, pics: dict[str, list[Sprite | Texture2D]]):
        alpha = pics.get(f'{name}_alpha')
        if alpha is not None:
            return alpha
        match = re.search(_variation_name_regex, name)
        if match is None:
            return None
        # e.g. pic_cbjms_3503_3 -> pic_cbjms_3503_alpha
        return pics.get(f'{name[:match.span()[0]]}_alpha')

    def _add_invalid(self, obj: ObjectReader | Sprite | Texture2D, reason: str):
        if obj.type.name == 'Sprite':
            self.invalid_path_id_index[obj.path_id] = (obj.container, reason)

    def _extract_pics(self, bundle: UnityPy.Environment, group: str):
        character: str | None = None
        pics: dict[str, list[Sprite | Texture2D]] = {}
        for obj in bundle.objects:
            if obj.type.name != 'Sprite' and obj.type.name != 'Texture2D':
                continue
            self.all_path_id_index[obj.path_id] = obj.container
            assert obj.container, f'{group} {obj.container}'
            match = _character_container_regex.match(obj.container)
            if match is None:
                match = _character_npc_regex.match(obj.container)
            if match is None:
                match = _character_fairy_regex.match(obj.container)
            if match is None:
                self._add_invalid(obj, 'container fails regex match')
                continue
            matched = match.group(1)

            if character is None:
                character = matched
            else:
                assert (
                    character == matched
                    or f'{character}_he' == matched
                    or character == f'{matched}_he'
                )

            name = match.group(2).lower()
            if not self.hd and (name.endswith('_hd') or name.endswith('_hd_alpha')):
                self._add_invalid(obj, 'hd')
                continue
            typed = typing.cast(Sprite | Texture2D, obj.read())
            pic = pics.get(name)
            if pic:
                assert len(pic) == 1 and pic[0].type.name != typed.type.name
                pic.append(typed)
            else:
                pics[name] = [typed]

        if group in ['boss', 'fairy']:
            character = group

        assert character is not None or any(
            c.endswith('.atlas.txt') or c.endswith('.skel.bytes') or c.endswith('.asset') or c.endswith('.mat') or
            any(sp in c for sp in _special_characters) for c in bundle.container.keys()
        ), bundle.container

        return character, pics

    def _process(self, bundle: UnityPy.Environment, group: str):
        character, pics = self._extract_pics(bundle, group)

        for name, pic in pics.items():
            assert len(pic) == 2 or (len(pic) == 1 and pic[0].type.name == 'Texture2D'), f'{name} {pic} {pics}'
            alpha_pic = self._try_alpha_names(name, pics)
            if alpha_pic is None:
                if name.endswith('_alpha'):
                    continue
                _warning('alpha resource for %s not found', name)
                if len(pic) == 1:
                    continue
                alpha_pic = []
            self._semaphore.acquire()
            threading.Thread(target=self._merge_image, args=(character, name, pic, alpha_pic)).start()

    def _merge_image(self, character: str, name: str, pic: list[Sprite | Texture2D], alpha_pic: list[Sprite | Texture2D]):
        if character is None or character == '':
            character = 'default'
        directory = self.destination.joinpath(character)
        os.makedirs(directory, exist_ok=True)
        if len(alpha_pic) == 0:
            file = self._save_sprite(directory, name, pic)
        else:
            file = self._merge_alpha_channel(
                directory,
                name,
                _get_texture(pic),
                _get_texture(alpha_pic),
            )

        if len(pic) == 2:
            path_id = _get_sprite_path_id(pic)
            assert path_id not in self.path_id_index
            self.path_id_index[path_id] = file
        else:
            _warning('sprite with path_id not found for %s (%s)', character, name)
        if character not in self.character_index:
            self.character_index[character] = []
        self.character_index[character].append(file)
        self._semaphore.release()

    def _save_sprite(self, directory: pathlib.Path, name: str, pic: list[Sprite | Texture2D]):
        image_path = directory.joinpath(f'{name}.png').resolve()
        if not self.force and image_path.exists():
            return image_path
        sprite = _get_pic_of_type(pic, 'Sprite')
        sprite.image.save(image_path)
        # pngquant to minimize the image
        if self.pngquant:
            quant_path = directory.joinpath(f'{name}.fs8.png')
            subprocess.run(['pngquant', image_path, '--ext', '.fs8.png', '--strip']).check_returncode()
            os.replace(quant_path, image_path)
        return image_path

    def _merge_alpha_channel(self, directory: pathlib.Path, name: str, sprite: Texture2D, alpha_sprite: Texture2D) -> pathlib.Path:
        image_path = directory.joinpath(f'{name}.png').resolve()
        if not self.force and image_path.exists():
            return image_path
        sprite_path = directory.joinpath(f'{name}.sprite.png')
        alpha_path = directory.joinpath(f'{name}.alpha.png')
        alpha_dims_path = directory.joinpath(f'{name}.dims.png')
        sprite.image.save(sprite_path)
        alpha_sprite.image.save(alpha_path)
        # resize to the same dimensions
        subprocess.run([
            'magick',
            sprite_path,
            '-set',
            'option:dims',
            '%wx%h',
            alpha_path,
            '-delete',
            '0',
            '-resize',
            '%[dims]',
            alpha_dims_path,
        ]).check_returncode()
        # copy the alpha channel
        subprocess.run([
            'convert',
            sprite_path,
            alpha_dims_path,
            '-compose',
            'copy-opacity',
            '-composite',
            image_path,
        ]).check_returncode()
        # remove intermediate files
        for file in (sprite_path, alpha_path, alpha_dims_path):
            os.remove(file)
        utils.pngquant(image_path, use_pngquant=self.pngquant)
        return image_path

    def load_files(self):
        for path in (bar := tqdm.tqdm(self.resource_files)):
            file = str(path)
            if 'atlasclips' in file:
                continue
            if file.endswith('resourcefairy.ab'):
                group = 'fairy'
            else:
                match = _character_file_regex.match(file)
                assert match, file
                group = match.group(1)
            if group in _special_files:
                continue
            bar.set_description(group)

            bundle = UnityPy.load(file)
            self._process(bundle, group)
        for _ in range(self.concurrency):
            self._semaphore.acquire()
        for _ in range(self.concurrency):
            self._semaphore.release()
