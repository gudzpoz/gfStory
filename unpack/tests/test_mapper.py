from gfunpack import characters
from gfunpack import mapper
from gfunpack import prefabs


def test_mapper():
    prefab_collection = prefabs.Prefabs('downloader/output', 'images')
    character_collection = characters.CharacterCollection('downloader/output', 'images', pngquant=True)
    mapping = mapper.Mapper(prefab_collection, character_collection)
    mapping.write_indices()


if __name__ == '__main__':
    test_mapper()
