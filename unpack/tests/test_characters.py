from gfunpack import characters


def test_characters():
    characters.CharacterCollection('downloader/output', 'images', pngquant=True)


if __name__ == '__main__':
    test_characters()
