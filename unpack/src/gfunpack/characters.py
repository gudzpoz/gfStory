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

from gfunpack import database, prefabs, utils

_logger = logging.getLogger('gfunpack.character')
_info = _logger.info
_warning = _logger.warning

_character_file_regex = re.compile('^.+character(.*)\\.ab$')


_alpha_postfixes = {
    'ar18/AR18_N_1.png': 'ar18/AR18_N_0.png',
    'ar18/AR18_N_2.png': 'ar18/AR18_N_0.png',
    'ar18/AR18_N_3.png': 'ar18/AR18_N_0.png',
    'ar18/AR18_N_4.png': 'ar18/pic_AR18.png',
    'npc-sakura/Pic_Sakura_D.png': 'npc-sakura/Pic_Sakura_D_1.png',
}


class CharacterCollection:
    directory: pathlib.Path

    destination: pathlib.Path

    required_path_ids: set[int]

    exported_images: dict[str, pathlib.Path]

    db: database.Database

    character_index: dict[str, list[pathlib.Path]]

    pngquant: bool

    force: bool

    concurrency: int

    verbose: bool

    _semaphore: threading.Semaphore

    _i: int

    def __init__(self, directory: str, destination: str, prefab_indices: prefabs.Prefabs,
                 pngquant: bool = False, force: bool = False, concurrency=8, verbose: bool = False):
        self.image_details = prefab_indices.details
        self.required_path_ids = set(
            i
            for details in prefab_indices.details.values()
            for detail in details
            for i in [detail.path_id, detail.alpha_path_id]
            if i != 0
        )
        self.directory = utils.check_directory(directory)
        self.destination = utils.check_directory(destination, create=True)
        db_path = str(self.destination.parent.joinpath('image.db').resolve())
        _info('database: %s', db_path)
        self.db = database.Database(db_path, directory)
        self._i = 0

        self.exported_images = {}
        self.character_index = {}
        self.pngquant = utils.test_pngquant(pngquant)
        self.force = force
        self.concurrency = concurrency
        self.verbose = verbose
        self._semaphore = threading.Semaphore(concurrency)
        self._test_commands()

    def _unique_id(self):
        self._i += 1
        return self._i

    def _test_commands(self) -> None:
        try:
            subprocess.run(['magick', '--help'], stdout=subprocess.DEVNULL).check_returncode()
        except FileNotFoundError as e:
            raise FileNotFoundError('imagemagick is required to merge alpha layers', e)

    def _extract_pics(self, bundle: UnityPy.Environment):
        """
        Extracts all the sprites and textures from the given bundle.
        """
        path_id_index: dict[int, Texture2D | Sprite] = {}
        for obj in bundle.objects:
            if obj.type.name != 'Sprite' and obj.type.name != 'Texture2D':
                continue
            if obj.path_id == 0 or obj.path_id not in self.required_path_ids:
                continue
            typed = typing.cast(Sprite | Texture2D, obj.read())
            path_id_index[obj.path_id] = typed
        return path_id_index

    @classmethod
    def _has_alpha_channel(cls, pics: list[pathlib.Path]):
        output = subprocess.check_output(
            ['magick', 'identify', '-format', '%[opaque]\\n']
            + [pic.resolve() for pic in pics],
            text=True,
        )
        return [line.lower() == 'false' for line in output.split('\n') if line != '']

    def _get_image_destination(self, character: str, name: str | None = None):
        directory = self.destination.joinpath(character)
        if name is None:
            return directory.resolve()
        return directory.joinpath(name).resolve()

    def _merge_alpha_channel(self, directory: pathlib.Path, name: str, path_id: int, key: str,
                             sprite: Texture2D, alpha_sprite: Texture2D):
        try:
            directory.mkdir(parents=True, exist_ok=True)
            image_path = directory.joinpath(f'{name}.png').resolve()
            self.exported_images[key] = image_path

            if not self.force and image_path.exists():
                return image_path
            i = self._unique_id()
            sprite_path = directory.joinpath(f'{name}.sprite-{i}.png')
            alpha_path = directory.joinpath(f'{name}.alpha-{i}.png')
            alpha_dims_path = directory.joinpath(f'{name}.dims-{i}.png')
            if alpha_sprite.name.endswith('_Alpha'):
                sprite.image.save(sprite_path)
                alpha_sprite.image.save(alpha_path)
                self._merge_files(sprite_path, alpha_path, alpha_dims_path, image_path)
                # remove intermediate files
                for file in (sprite_path, alpha_path, alpha_dims_path):
                    os.remove(file)
            else:
                alpha_sprite.image.save(image_path)
                if not self._has_alpha_channel([image_path])[0]:
                    sprite.image.save(image_path)
                if not self._has_alpha_channel([image_path])[0]:
                    _warning('no alpha channel: %s', image_path)
            utils.pngquant(image_path, use_pngquant=self.pngquant)
        finally:
            self._semaphore.release()

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
            sprite_path,
            alpha_dims_path,
            '-compose',
            'copy-opacity',
            '-composite',
            image_path,
        ]).check_returncode()

    def read_single(self, info: database.Image):
        path = self.db.get_bundle_path(info.bundle)
        bundle = UnityPy.load(str(path))
        for obj in bundle.objects:
            if obj.path_id == info.path_id:
                return typing.cast(Texture2D | Sprite, obj.read())
        raise ValueError(f'no object at path_id {info.path_id}')

    def _try_merging_alpha(self, path_id_index: dict[int, Texture2D | Sprite], sprites: list[int]):
        for character, details in (bar := tqdm.tqdm(self.image_details.items())):
            bar.set_description(character)
            for i, detail in enumerate(details):
                assert character.lower() == detail.name.lower()
                path_id = detail.path_id
                alpha_path_id = detail.alpha_path_id
                if path_id not in path_id_index:
                    path_id = 0
                if alpha_path_id not in path_id_index:
                    alpha_path_id = 0
                if path_id == 0:
                    if alpha_path_id == 0:
                        _warning(f'no image at all: {character}: {detail}')
                        continue
                    alpha = path_id_index[alpha_path_id]
                    if alpha.name.endswith('_Alpha'):
                        name = alpha.name[:-6]
                        info = self.db.find_by_name(name)
                        if info is None:
                            _warning(f'no image for _Alpha: {character}: {name} {detail}')
                            continue
                        path_id_index[info.path_id] = self.read_single(info)
                        path_id = info.path_id
                        detail.path_id = path_id
                    else:
                        path_id = alpha_path_id
                        detail.path_id = alpha_path_id
                if alpha_path_id == 0:
                    _warning(f'no alpha channel: {character}: {detail}')
                    alpha_path_id = path_id
                self._semaphore.acquire()
                image = path_id_index[path_id]
                alpha_image = path_id_index[alpha_path_id]
                name = image.name
                assert name is not None and name != ''
                threading.Thread(
                    target=self._merge_alpha_channel,
                    args=(
                        self._get_image_destination(character.lower()),
                        name,
                        path_id,
                        f'{character}/{i}',
                        image,
                        alpha_image,
                    ),
                ).start()

        for _ in range(self.concurrency):
            self._semaphore.acquire(timeout=120/self.concurrency)
        for _ in range(self.concurrency):
            self._semaphore.release()

    def _postfix(self):
        image = self._get_image_destination('npc-sakura', 'Pic_Sakura_D.png')
        if not self._has_alpha_channel([image])[0]:
            source = image.rename(image.with_suffix('.tmp.png'))
            # crop the image, parameters manually acquired
            subprocess.run([
                'magick',
                source,
                '-crop',
                '809x1367+782+13',
                image,
            ]).check_returncode()
            source.unlink()
        for image_name, alpha_name in _alpha_postfixes.items():
            image = self._get_image_destination(image_name)
            alpha = self._get_image_destination(alpha_name)
            source = image.with_suffix('.tmp.png')
            dims = image.with_suffix('.dims.png')
            image.rename(source)
            self._merge_files(source, alpha, dims, image)
            for f in [source, dims]:
                f.unlink()

    def extract(self):
        l = list(self.required_path_ids)
        images = self.db.get_by_path_ids(l)
        sprites = self.db.get_by_path_ids(l, True)
        bundles = set(image.bundle for image in images).union(
            set(sprite.bundle for sprite in sprites),
        )
        path_id_index: dict[int, Texture2D | Sprite] = {}
        for bundle_name in (bar := tqdm.tqdm(bundles)):
            path = self.db.get_bundle_path(bundle_name)
            file = str(path)
            if file.endswith('resourcefairy.ab'):
                group = 'fairy'
            else:
                # Group images by character names
                match = _character_file_regex.match(file)
                group = bundle_name[36:] if match is None else match.group(1)
            bar.set_description(group)
            bundle = UnityPy.load(file)
            extracted = self._extract_pics(bundle)
            for path_id, img in extracted.items():
                if path_id in path_id_index and 'avgpicprefab' in bundle_name:
                    continue
                path_id_index[path_id] = img

        if path_id_index.keys() != self.required_path_ids:
            non_alpha_ids = set(
                detail.path_id
                for details in self.image_details.values()
                for detail in details
                if detail.path_id != 0
            )
            # transparency already merged into the alpha image
            assert (self.required_path_ids - path_id_index.keys()).issubset(non_alpha_ids)
        self._try_merging_alpha(path_id_index, [s.path_id for s in sprites])
        self._postfix()
