from gfunpack import characters, prefabs


def test_characters():
    sprite_indices = prefabs.Prefabs('downloader/output')
    characters.CharacterCollection(
        'downloader/output', 'images',
        sprite_indices, pngquant=True,
    ).extract()


if __name__ == '__main__':
    test_characters()
