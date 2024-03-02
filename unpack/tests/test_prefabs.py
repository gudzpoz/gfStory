from gfunpack import prefabs


def test_collecting_files():
    prefabs.Prefabs('downloader/output', 'images')


if __name__ == '__main__':
    test_collecting_files()
