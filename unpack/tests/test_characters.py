from gfunpack import characters


def test_characters():
    characters.CharacterCollection('output', 'pics', pngquant=True)


if __name__ == '__main__':
    test_characters()
