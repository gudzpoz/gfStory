from gfunpack import characters
from gfunpack import mapper
from gfunpack import prefabs


def test_mapper():
    prefab_collection = prefabs.Prefabs('downloader/output')
    character_collection = characters.CharacterCollection(
        'downloader/output', 'images', prefab_collection,
        pngquant=True, verbose=True,
    )
    character_collection.extract()
    mapping = mapper.Mapper(prefab_collection, character_collection)
    mapping.write_indices()


if __name__ == '__main__':
    test_mapper()
