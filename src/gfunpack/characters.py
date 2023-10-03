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

from gfunpack import utils

_logger = logging.getLogger('gfunpack.character')
_warning = _logger.warning

_character_file_regex = re.compile('^.+character(.*)\\.ab$')
_character_container_regex = re.compile('^assets/characters/([^/]+)/pic(?:_he)?/([^/]+)\\.png$')
_character_npc_regex = re.compile('^assets/characters/([^/]+)/([^/]+)\\.png$')


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

    path_id_index: dict[int, str]

    character_index: dict[str, list[str]]

    hd: bool

    pngquant: bool

    force: bool

    _concurrency: threading.Semaphore

    def __init__(self, directory: str, destination: str,
                 hd: bool = False, pngquant: bool = False, force: bool = False, concurrency = 8) -> None:
        self.directory = utils.check_directory(directory)
        self.destination = utils.check_directory(destination, create=True)
        self.path_id_index = {}
        self.character_index = {}
        self.hd = hd
        self.pngquant = pngquant
        self.force = force
        self._concurrency = threading.Semaphore(concurrency)
        self.resource_files = [path for path in self.directory.glob('*character*.ab') if 'spine' not in str(path)]
        self._test_commands()
        self.load_files()

    def _test_commands(self) -> None:
        try:
            subprocess.run(['magick', '--help'], stdout=subprocess.DEVNULL).check_returncode()
            subprocess.run(['convert', '-version'], stdout=subprocess.DEVNULL).check_returncode()
            if self.pngquant:
                subprocess.run(['pngquant', '--help'], stdout=subprocess.DEVNULL).check_returncode()
        except FileNotFoundError as e:
            raise FileNotFoundError('imagemagick is required to merge alpha layers, pngquant is optional', e)

    def _process(self, bundle: UnityPy.Environment, group: str):
        character: str | None = None
        pics: dict[str, list[Sprite | Texture2D]] = {}
        for obj in bundle.objects:
            if obj.type.name != 'Sprite' and obj.type.name != 'Texture2D':
                continue
            assert obj.container, f'{group} {obj.container}'
            match = _character_container_regex.match(obj.container)
            if match is None:
                match = _character_npc_regex.match(obj.container)
                if match is None:
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
                continue
            typed = typing.cast(Sprite | Texture2D, obj.read())
            pic = pics.get(name)
            if pic:
                assert len(pic) == 1 and pic[0].type.name != typed.type.name
                pic.append(typed)
            else:
                pics[name] = [typed]

        if group in ['boss']:
            character = group

        assert character is not None or any(
            c.endswith('.atlas.txt') or c.endswith('.skel.bytes') or c.endswith('.asset') or c.endswith('.mat') or
            any(sp in c for sp in _special_characters) for c in bundle.container.keys()
        ), bundle.container

        for name, pic in pics.items():
            assert len(pic) == 2 or (len(pic) == 1 and pic[0].type.name == 'Texture2D'), f'{name} {pic} {pics}'
            alpha_pic = pics.get(f'{name}_alpha')
            if alpha_pic is None:
                continue
            self._concurrency.acquire()
            threading.Thread(target=self._merge_image, args=(character, name, pic, alpha_pic)).start()
            self._concurrency.release()
    
    def _merge_image(self, character: str, name: str, pic: list[Sprite | Texture2D], alpha_pic: list[Sprite | Texture2D]):
        if character is None or character == '':
            character = 'default'
        self._concurrency.acquire()
        file = self._merge_alpha_channel(
            character,
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
        self._concurrency.release()

    def _merge_alpha_channel(self, character: str, name: str, sprite: Texture2D, alpha_sprite: Texture2D) -> str:
        directory = self.destination.joinpath(character)
        os.makedirs(directory, exist_ok=True)
        image_path = directory.joinpath(f'{name}.png').resolve()
        if not self.force and image_path.exists():
            return str(image_path)
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
        # pngquant to minimize the image
        if self.pngquant:
            quant_path = directory.joinpath(f'{name}.fs8.png')
            subprocess.run(['pngquant', image_path, '--ext', '.fs8.png', '--strip']).check_returncode()
            os.replace(quant_path, image_path)
        return str(image_path)

    def load_files(self):
        for path in (bar := tqdm.tqdm(self.resource_files)):
            file = str(path)
            if 'atlasclips' in file:
                continue
            match = _character_file_regex.match(file)
            assert match, file
            group = match.group(1)
            if group in _special_files:
                continue
            bar.set_description(group)

            bundle = UnityPy.load(file)
            self._process(bundle, group)
