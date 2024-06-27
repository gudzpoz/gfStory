import json
import logging
import dataclasses
import pathlib
import typing

from gfunpack.characters import CharacterCollection
from gfunpack.prefabs import DialoguePicDetails, Prefabs

_logger = logging.getLogger('gfunpack.prefabs')
_warning = _logger.warning


@dataclasses.dataclass
class SpriteDetails:
    path: pathlib.Path
    scale: float = -1.0
    offset: tuple[float, float] = (0.0, 0.0)


class Mapper:
    prefabs: Prefabs

    characters: CharacterCollection

    mapped: dict[str, dict[int, dict]]

    def __init__(self, prefabs: Prefabs, characters: CharacterCollection):
        self.prefabs = prefabs
        self.characters = characters
        self.mapped = {}
        self.map_sprite_path_ids()

    def _map_pic(self, character: str, i: int):
        result = self.characters.exported_images.get(f'{character}/{i}')
        return result

    def _add_mapped(self, name: str, i: int, d: SpriteDetails | DialoguePicDetails):
        dest = self.mapped
        asdict = dataclasses.asdict(d)
        sprite_details = typing.cast(SpriteDetails, d)
        asdict['path'] = str(sprite_details.path.relative_to(self.characters.destination))
        if name not in dest:
            dest[name] = {}
        dest[name][i] = asdict

    def map_sprite_path_ids(self):
        mapped_paths: list[pathlib.Path] = []
        for name, details in self.prefabs.details.items():
            for i, detail in enumerate(details):
                path = None if detail.path_id == 0 else self._map_pic(name, i)
                if detail.path_id == 0:
                    _warning('%s (%d) (with empty path_id) not processed', name, i)
                    continue
                elif path == None:
                    _warning('%s (%d) (path_id=%d) path_id not found', name, i, detail.path_id)
                    continue
                self._add_mapped(name, i, SpriteDetails(path, detail.scale, detail.offset))
                mapped_paths.append(path.resolve())

        extracted = set(path.resolve() for path in self.characters.destination.glob('*/*.png'))
        remaining: list[pathlib.Path] = sorted(
            path for path in (extracted - set(mapped_paths))
        )
        if len(remaining) > 0:
            categorized = {}
            for path in remaining:
                if path.parent.name == 'background':
                    continue
                name, path = path.parts[-2:]
                categorized.setdefault(name, []).append(path)
            _warning('%d remaining images: %s', len(remaining), categorized)

    def write_indices(self):
        data = self.mapped
        path = self.characters.destination.joinpath(f'mapped.json')
        with open(path, 'w') as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False))
        path.rename(self.characters.destination.joinpath('characters.json'))
