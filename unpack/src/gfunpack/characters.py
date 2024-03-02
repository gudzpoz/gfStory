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


def _get_pic_of_type(pics: list[Sprite | Texture2D],
                     t: typing.Literal['Sprite'] | typing.Literal['Texture2D']) -> (Sprite | Texture2D):
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

_special_alpha_mapping = {
    'nytochild04': 'nyto_child/nytochild01_1.png',
}


class CharacterCollection:
    directory: pathlib.Path

    destination: pathlib.Path

    resource_files: list[pathlib.Path]

    extra_alpha_resources: dict[str, Texture2D]

    path_id_index: dict[int, pathlib.Path]

    invalid_path_id_index: dict[int, tuple[pathlib.Path, str]]

    all_path_id_index: dict[int, pathlib.Path]

    character_index: dict[str, list[pathlib.Path]]

    alpha_not_found: list[pathlib.Path]

    hd: bool

    pngquant: bool

    force: bool

    concurrency: int

    _semaphore: threading.Semaphore

    def __init__(self, directory: str, destination: str,
                 hd: bool = False, pngquant: bool = False, force: bool = False, concurrency=8) -> None:
        self.directory = utils.check_directory(directory)
        self.destination = utils.check_directory(destination, create=True)
        self.path_id_index = {}
        self.invalid_path_id_index = {}
        self.all_path_id_index = {}
        self.character_index = {}
        self.alpha_not_found = []
        self.hd = hd
        self.pngquant = utils.test_pngquant(pngquant)
        self.force = force
        self.concurrency = concurrency
        self._semaphore = threading.Semaphore(concurrency)
        self.resource_files = []
        self.resource_files.extend(self.directory.glob('*resourcefairy.ab'))
        self.resource_files.extend(path for path in self.directory.glob('*character*.ab') if 'spine' not in str(path))
        self.extra_alpha_resources = self._index_alpha_images(list(self.directory.glob('*prefab*.ab')))
        self._test_commands()
        self.load_files()

    def _test_commands(self) -> None:
        try:
            subprocess.run(['magick', '--help'], stdout=subprocess.DEVNULL).check_returncode()
        except FileNotFoundError as e:
            raise FileNotFoundError('imagemagick is required to merge alpha layers', e)

    @classmethod
    def _index_alpha_images(cls, resources: list[pathlib.Path]):
        images: dict[str, Texture2D] = {}
        for path in resources:
            asset = UnityPy.load(str(path))
            for o in asset.objects:
                if o.type.name == 'Texture2D':
                    data = typing.cast(Texture2D, o.read())
                    images[data.name.lower()] = data
        return images

    def _try_alpha_names(self, name: str, pics: dict[str, list[Sprite | Texture2D]]):
        alpha_name = f'{name}_alpha'
        alpha = pics.get(alpha_name)
        if alpha is not None:
            return alpha
        extra = self.extra_alpha_resources.get(alpha_name.lower())
        if extra is not None:
            return [extra]
        if name.endswith('_alpha'):
            return None

        match = re.search(_variation_name_regex, name)
        if match is not None:
            # e.g. pic_cbjms_3503_3 -> pic_cbjms_3503_alpha
            name = name[:match.span()[0]]
            alpha_name = f'{name}_alpha'
            alpha = pics.get(alpha_name)
            if alpha is not None:
                return alpha
            extra = self.extra_alpha_resources.get(alpha_name.lower())
            if extra is not None:
                return [extra]

        candidates = [k for k in pics.keys() if k.startswith(name) and k.endswith('_alpha')]
        if len(candidates) == 0:
            i = name.rfind('_')
            if i != -1:
                name = name[:i]
                candidates = [k for k in pics.keys() if k.startswith(name) and k.endswith('_alpha')]
        if len(candidates) == 0:
            i = name.rfind('(')
            if i != -1:
                name = name[:i]
                candidates = [k for k in pics.keys() if k.startswith(name) and k.endswith('_alpha')]
        if len(candidates) == 0:
            if not name.startswith('pic_'):
                name = 'pic_' + name
                candidates = [k for k in pics.keys() if k.startswith(name) and k.endswith('_alpha')]
        candidates.sort()
        return None if len(candidates) == 0 else pics[candidates[0]]

    def _add_invalid(self, obj: ObjectReader | Sprite | Texture2D, reason: str):
        if obj.type.name == 'Sprite':
            self.invalid_path_id_index[obj.path_id] = (obj.container, reason)

    def _extract_pics(self, bundle: UnityPy.Environment, group: str):
        """
        Extracts all the sprites and textures from the given bundle,
        grouping similar Sprite and Texture2D assets together.
        """
        character: str | None = None
        # pics: dict[character_name, [sprite, texture2d]]
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
            # matched = character_name (probably)
            matched = match.group(1)

            if character is None:
                character = matched
            else:
                assert (
                    character == matched
                    or f'{character}_he' == matched
                    or character == f'{matched}_he'
                )

            # image variation name
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

        files: set[str] = set()

        for name, pic in pics.items():
            assert len(pic) == 2 or (len(pic) == 1 and pic[0].type.name == 'Texture2D'), f'{name} {pic} {pics}'
            # names ending with alpha does not imply an alpha file, since there may be dolls named alpha...
            alpha_pic = self._try_alpha_names(name, pics)
            if alpha_pic is None:
                if name.endswith('_alpha'):
                    continue
                if len(pic) == 1:
                    # Texture2D usually does not contain a in-file alpha channel.
                    # While Sprite files usually comes with a Texture2D file.
                    _warning('alpha resource for %s not found', name)
                    continue
                alpha_pic = []
            file = f'{character}/{name}'
            if file in files:
                _warning('ignoring dup resource for %s', name)
                continue
            files.add(file)
            self._semaphore.acquire()
            threading.Thread(target=self._merge_image, args=(character, name, pic, alpha_pic)).start()

    def _has_alpha_channel(cls, pic: pathlib.Path):
        output = subprocess.check_output(['magick', 'identify', '-format', '%[opaque]', pic.resolve()], text=True)
        return output.strip().lower() == 'false'

    def _get_image_destination(self, character: str, name: str | None = None):
        directory = self.destination.joinpath(character)
        if name is None:
            return directory.resolve()
        return directory.joinpath(name).resolve()

    def _merge_image(self, character: str, name: str, pic: list[Sprite | Texture2D],
                     alpha_pic: list[Sprite | Texture2D]):
        try:
            if character is None or character == '':
                character = 'default'
            directory = self._get_image_destination(character)
            os.makedirs(directory, exist_ok=True)
            if len(alpha_pic) == 0:
                file = self._save_sprite(directory, name, pic)
                if not self._has_alpha_channel(file):
                    self.alpha_not_found.append(file.resolve())
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
        finally:
            self._semaphore.release()

    def _save_sprite(self, directory: pathlib.Path, name: str, pic: list[Sprite | Texture2D]):
        image_path = directory.joinpath(f'{name}.png').resolve()
        if not self.force and image_path.exists():
            return image_path
        sprite = _get_pic_of_type(pic, 'Sprite')
        sprite.image.save(image_path)
        # pngquant to minimize the image
        utils.pngquant(image_path, use_pngquant=self.pngquant)
        return image_path

    def _merge_alpha_channel(self, directory: pathlib.Path, name: str,
                             sprite: Texture2D, alpha_sprite: Texture2D) -> pathlib.Path:
        image_path = directory.joinpath(f'{name}.png').resolve()
        if not self.force and image_path.exists():
            return image_path
        sprite_path = directory.joinpath(f'{name}.sprite.png')
        alpha_path = directory.joinpath(f'{name}.alpha.png')
        alpha_dims_path = directory.joinpath(f'{name}.dims.png')
        sprite.image.save(sprite_path)
        alpha_sprite.image.save(alpha_path)
        self._merge_files(sprite_path, alpha_path, alpha_dims_path, image_path)
        # remove intermediate files
        for file in (sprite_path, alpha_path, alpha_dims_path):
            os.remove(file)
        utils.pngquant(image_path, use_pngquant=self.pngquant)
        return image_path

    @classmethod
    def _merge_files(cls, sprite_path: pathlib.Path, alpha_path: pathlib.Path,
                     alpha_dims_path: pathlib.Path, image_path: pathlib.Path):
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
            'magick',
            'convert',
            sprite_path,
            alpha_dims_path,
            '-compose',
            'copy-opacity',
            '-composite',
            image_path,
        ]).check_returncode()

    def _try_finding_alpha(self, file: pathlib.Path, stem: str):
        damaged = stem.endswith('_d')

        def glob(directory: pathlib.Path, pattern: str):
            nonlocal damaged
            return sorted(f for f in directory.glob(pattern)
                          if f.stem.endswith('_d') == damaged and self._has_alpha_channel(f))

        if stem in _special_alpha_mapping:
            return [self.destination.joinpath(_special_alpha_mapping[stem])]
        candidates = []
        if len(candidates) == 0:
            candidates = glob(self.destination, f'*/{stem}.png')
        if len(candidates) == 0:
            candidates = glob(self.destination, f'*/pic_{stem}.png')
        if len(candidates) == 0:
            candidates = glob(self.destination, f'*/pic_{stem}_*.png')
        if len(candidates) == 0:
            if stem[-1].isdigit():
                digitless = re.match('^(.*[^\\d])\\d+$', stem)
                if digitless is not None:
                    candidates = glob(file.parent, f'{digitless.group(1)}*.png')
        if len(candidates) == 0:
            digitless = re.match('^(.*[^_])_+m_*$', stem)
            if digitless is not None:
                candidates = glob(file.parent, f'{digitless.group(1)}*.png')
        if len(candidates) == 0:
            if stem.endswith('_he'):
                return self._try_finding_alpha(file, stem[:-2])
            if '_he_' in stem:
                return self._try_finding_alpha(file, stem.replace('_he_', '_'))
        return candidates

    def _try_merging_alpha(self):
        not_found = set(self.alpha_not_found)
        found: list[pathlib.Path] = []
        file: pathlib.Path
        for file in self.alpha_not_found:
            stem = file.stem
            i = stem.rfind('(')
            if i == -1:
                i = stem.rfind('_')
            if i == -1:
                i = len(stem)
            stem = stem[:i]
            candidates = self._try_finding_alpha(file, stem)
            for candidate in candidates:
                if candidate not in not_found:
                    _warning('attempt to use %s as alpha for %s', candidate, file)
                    dims_path = file.with_stem(f'{stem}.dims')
                    image_path = file.with_stem(f'{stem}.output')
                    self._merge_files(file, candidate, dims_path, image_path)
                    dims_path.unlink()
                    image_path.replace(file)
                    found.append(file)
                    break
        _warning('no alpha files found for \n%s', '\n'.join(sorted(map(str, not_found - set(found)))))

    def load_files(self):
        for path in (bar := tqdm.tqdm(self.resource_files)):
            file = str(path)
            if 'atlasclips' in file:
                continue
            if file.endswith('resourcefairy.ab'):
                group = 'fairy'
            else:
                # Group images by character names
                match = _character_file_regex.match(file)
                assert match, file
                group = match.group(1)
            if group in _special_files:
                continue
            bar.set_description(group)

            bundle = UnityPy.load(file)
            self._process(bundle, group)
        for _ in range(self.concurrency):
            self._semaphore.acquire(timeout=120/self.concurrency)
        for _ in range(self.concurrency):
            self._semaphore.release()
        self._try_merging_alpha()
