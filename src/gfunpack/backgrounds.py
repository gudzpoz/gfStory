import json
import logging
import pathlib
import re
import threading
import typing

import tqdm
import UnityPy
from UnityPy.classes import Sprite, TextAsset, Texture2D

from gfunpack import utils

_logger = logging.getLogger('gfunpack.utils')
_warning = _logger.warning

_avgtexture_regex = re.compile('^assets/resources/dabao/avgtexture/([^/]+)\\.png$')


class BackgroundCollection:
    directory: pathlib.Path

    destination: pathlib.Path

    profile_asset: pathlib.Path

    resource_files: list[pathlib.Path]

    extracted: dict[int, pathlib.Path | None]

    pngquant: bool

    force: bool

    concurrency: int

    _semaphore: threading.Semaphore

    def __init__(self, directory: str, destination: str, pngquant: bool = False, force: bool = False, concurrency: int = 8) -> None:
        self.directory = utils.check_directory(directory)
        self.destination = utils.check_directory(pathlib.Path(destination).joinpath('background'), create=True)
        self.pngquant = utils.test_pngquant(pngquant)
        self.force = force
        self.concurrency = concurrency
        self._semaphore = threading.Semaphore(concurrency)
        self.profile_asset = list(self.directory.glob('*assettextavg.ab'))[0]
        self.resource_files = list(self.directory.glob('*resourceavgtexture*.ab'))
        self.extracted = self.extract()

    def _extract_bg_profiles(self) -> list[str]:
        asset = UnityPy.load(str(self.profile_asset))
        profile_reader = [o for o in asset.objects if o.container == 'assets/resources/dabao/avgtxt/profiles.txt'][0]
        assert profile_reader.type.name == 'TextAsset'
        profile = typing.cast(
            TextAsset,
            profile_reader.read()
        )
        content: str = profile.m_Script.tobytes().decode()
        return [l.strip() for l in content.split('\n')]

    def _save_image(self, extracted: dict[str, pathlib.Path], name: str, image: Sprite | Texture2D):
        image_path = self.destination.joinpath(f'{name}.png')
        if self.force or not image_path.is_file():
            image.image.save(image_path)
            utils.pngquant(image_path, use_pngquant=self.pngquant)
        extracted[name] = image_path
        self._semaphore.release()
    
    def _extract_files(self, resources: dict[str, Sprite | Texture2D]):
        extracted: dict[str, pathlib.Path] = {}
        for name, image in resources.items():
            self._semaphore.acquire()
            threading.Thread(target=self._save_image, args=(extracted, name, image)).start()
        for _ in range(self.concurrency):
            self._semaphore.acquire()
        for _ in range(self.concurrency):
            self._semaphore.release()
        return extracted
    
    def _extract_bg_pics(self):
        extracted: dict[str, pathlib.Path] = {}
        for file in tqdm.tqdm(self.resource_files):
            files: dict[str, Sprite | Texture2D] = {}
            asset = UnityPy.load(str(file))
            for o in asset.objects:
                if o.container is None:
                    continue
                if o.type.name != 'Sprite' and o.type.name != 'Texture2D':
                    continue
                match = _avgtexture_regex.match(o.container)
                if match is None:
                    continue
                name = match.group(1).lower()
                data = typing.cast(Sprite | Texture2D, o.read())
                if name not in files:
                    files[name] = data
                else:
                    # prioritize Texture2D assets
                    if files[name].type.name == 'Sprite':
                        files[name] = data
            extracted.update(self._extract_files(files))
        return extracted

    def extract(self):
        bg_profiles = self._extract_bg_profiles()
        pics = self._extract_bg_pics()
        merged: dict[int, pathlib.Path | None] = {}
        matched: list[pathlib.Path] = []
        for i, name in enumerate(bg_profiles):
            match = pics.get(name.lower())
            merged[i] = match
            if match is not None:
                matched.append(match.resolve())
            else:
                _warning('bg %s not found', name)
        unmatched = set(p.resolve() for p in pics.values()) - set(matched)
        for path in unmatched:
            merged[-len(merged)] = path
        return merged

    def save(self):
        s = json.dumps(
            dict((k, "" if v is None else str(v.relative_to(self.destination))) for k, v in self.extracted.items()),
            ensure_ascii=False,
            indent=2,
        )
        path = self.destination.parent.joinpath('backgrounds.json')
        with path.open('w') as f:
            f.write(s)
        return path
