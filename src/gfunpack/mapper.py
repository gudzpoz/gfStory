import json
import logging
import dataclasses
import typing

from gfunpack.characters import CharacterCollection
from gfunpack.prefabs import DialoguePicDetails, Prefabs

_logger = logging.getLogger('gfunpack.prefabs')
_warning = _logger.warning


@dataclasses.dataclass
class SpriteDetails:
    path: str
    scale: float
    offset: tuple[float, float]


class Mapper:
    prefabs: Prefabs

    characters: CharacterCollection

    mapped: dict[str, dict[int, dict]]

    unmapped: dict[str, dict[int, dict]]

    remaining: dict[str, list[str]]

    def __init__(self, prefabs: Prefabs, characters: CharacterCollection):
        self.prefabs = prefabs
        self.characters = characters
        self.mapped = {}
        self.unmapped = {}
        self.remaining = {}
        self.map_sprite_path_ids()

    def _map_pic(self, details: DialoguePicDetails):
        path_id = details.path_id
        return self.characters.path_id_index.get(path_id)
    
    def _add_mapped(self, name: str, i: int, d: dict, mapped: bool):
        dest = self.mapped if mapped else self.unmapped
        if name not in dest:
            dest[name] = {}
        dest[name][i] = d

    def map_sprite_path_ids(self):
        mapped_paths: list[str] = []
        for i, (name, details) in enumerate(self.prefabs.details.items()):
            for detail in details:
                detail_dict = dataclasses.asdict(detail)
                if detail.path_id == 0:
                    _warning('%s (%d) (with empty path_id) not processed', name, i)
                    self._add_mapped(name, i, detail_dict, False)
                    continue
                path = self._map_pic(detail)
                if path is None:
                    _warning('%s (%d) (path_id=%d) path_id not found', name, i, detail.path_id)
                    self._add_mapped(name, i, detail_dict, False)
                    continue
                self._add_mapped(name, i, dataclasses.asdict(SpriteDetails(path, detail.scale, detail.offset)), True)
                mapped_paths.append(path)
        
        extracted = set(str(path.resolve()) for path in self.characters.destination.glob('**/*.png'))
        remaining: list[tuple[str, str]] = sorted(
            typing.cast(tuple[str, str], tuple(path.rsplit('/', 2)[-2:]))
            for path in (extracted - set(mapped_paths))
        )
        for directory, file in remaining:
            if directory not in self.remaining:
                self.remaining[directory] = []
            self.remaining[directory].append(file)

    def write_indices(self):
        for name in ['mapped', 'unmapped', 'remaining']:
            data = getattr(self, name)
            with open(self.characters.destination.joinpath(f'{name}.json'), 'w') as f:
                f.write(json.dumps(data, indent=2))
