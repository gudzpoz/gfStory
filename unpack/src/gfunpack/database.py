import dataclasses
import logging
import sqlite3
import typing
from pathlib import Path

import tqdm
import UnityPy
from UnityPy.classes import Sprite, Texture2D


_logger = logging.getLogger('gfunpack.database')
_warning = _logger.warning


@dataclasses.dataclass
class Image:
    path_id: int
    name: str
    is_sprite: int
    width: int
    height: int
    bundle: str
    container: str

_image_fields = 'path_id, name, is_sprite, width, height, bundle, container'
_image_field_placeholders = ', '.join(['?'] * len(_image_fields.split(',')))


def to_image(data: tuple | None):
    return None if data is None else Image(*data)


class Database:
    db: sqlite3.Connection

    bundles: list[Path]

    directory: Path

    _initialized: bool

    def __init__(self, db: str, directory: str):
        self.bundles = list(Path(directory).glob('*.ab'))
        self.directory = Path(directory)
        self.db = sqlite3.connect(db)
        self._initialized = False

    def close(self):
        self.db.close()

    def get_bundle_path(self, bundle: str) -> Path:
        return self.directory.joinpath(f'{bundle}.ab')

    @classmethod
    def _get_bundles(cls, cur: sqlite3.Cursor) -> list[tuple[str, int]]:
        res = cur.execute('SELECT name, size FROM bundle')
        return res.fetchall()

    def _init(self):
        if self._initialized:
            return
        cur = self.db.cursor()
        try:
            cur.execute('CREATE TABLE IF NOT EXISTS bundle (name TEXT PRIMARY KEY, size INTEGER)')
            cur.execute('CREATE TABLE IF NOT EXISTS image ('
                        'id INTEGER PRIMARY KEY,'
                        'path_id INTEGER,'
                        'name TEXT,'
                        'is_sprite INTEGER,'
                        'width INTEGER,'
                        'height INTEGER,'
                        'bundle TEXT,'
                        'container TEXT'
                        ')')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_image_path_id ON image (path_id)')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_image_bundle ON image (bundle)')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_image_name ON image (name)')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_image_container ON image (container)')

            db_bundles = set(self._get_bundles(cur))
            now_bundles = set((b.stem, b.stat().st_size) for b in self.bundles)
            removed_bundles = db_bundles - now_bundles
            new_bundles = set(b for b, _ in now_bundles - db_bundles)
            if len(removed_bundles) > 0:
                cur.execute(f'''DELETE FROM bundle WHERE name IN ({
                    ', '.join('?' * len(removed_bundles))
                })''', [b for b, _ in removed_bundles])
                cur.execute('DELETE FROM image WHERE bundle NOT IN (SELECT name FROM bundle)')

            new_records: list[Image] = []
            for path in tqdm.tqdm(self.bundles):
                if path.stem not in new_bundles:
                    continue
                bundle = UnityPy.load(str(path))
                for obj in bundle.objects:
                    if obj.type.name == 'Texture2D':
                        image = typing.cast(Texture2D, obj.read())
                        info = Image(
                            image.path_id,
                            image.name,
                            0,
                            image.m_Width,
                            image.m_Height,
                            path.stem,
                            str(image.get('container', '')),
                        )
                    elif obj.type.name == 'Sprite':
                        image = typing.cast(Sprite, obj.read())
                        info = Image(
                            image.path_id,
                            image.name,
                            1,
                            int(image.m_Rect.width),
                            int(image.m_Rect.height),
                            path.stem,
                            str(image.get('container', '')),
                        )
                    else:
                        continue
                    new_records.append(info)

            if len(new_records) > 0:
                cur.executemany(
                    f'INSERT INTO image ({_image_fields}) VALUES ({_image_field_placeholders})',
                    ((r.path_id, r.name, r.is_sprite, r.width, r.height, r.bundle, r.container) for r in new_records),
                )
            cur.executemany(
                'INSERT INTO bundle (name, size) VALUES (?, ?)',
                list(now_bundles - db_bundles),
            )
        finally:
            cur.close()
            self.db.commit()
        self._initialized = True

    def get_all_images(self) -> list[Image]:
        self._init()
        cur = self.db.cursor()
        try:
            cur.execute(f'SELECT {_image_fields} FROM image')
            return [Image(*r) for r in cur.fetchall()]
        finally:
            cur.close()

    def get_by_path_ids(self, path_id: list[int], sprite: bool = False) -> list[Image]:
        self._init()
        cur = self.db.cursor()
        try:
            images: list[Image] = []
            for i in range(0, len(path_id), 1000):
                batch = path_id[i : i+1000]
                res = cur.execute(
                    f'''SELECT {_image_fields} FROM image WHERE path_id IN ({
                        ', '.join('?' * len(batch))
                    }) AND is_sprite = {'1' if sprite else '0'}''',
                    batch,
                )
                images.extend(Image(*r) for r in res.fetchall())
            return images
        finally:
            cur.close()

    def find_by_name(self, name: str):
        self._init()
        cur = self.db.cursor()
        try:
            res = cur.execute(
                f'SELECT {_image_fields} FROM image WHERE name = ? AND is_sprite = 0',
                (name,),
            )
            return to_image(res.fetchone())
        finally:
            cur.close()

    def find_sprite_by_id(self, path_id: int):
        self._init()
        cur = self.db.cursor()
        try:
            res = cur.execute(
                f'SELECT {_image_fields} FROM image WHERE path_id = ? AND is_sprite = 1',
                (path_id,),
            )
            return to_image(res.fetchone())
        finally:
            cur.close()
