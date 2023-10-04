from gfunpack import backgrounds


def test_backgrounds():
    bg = backgrounds.BackgroundCollection('downloader/output', 'images', pngquant=True)
    bg.save()


if __name__ == '__main__':
    test_backgrounds()
