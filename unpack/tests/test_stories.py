from gfunpack import stories


def test_stories():
    s = stories.Stories('downloader/output', 'stories')
    s.save()


if __name__ == '__main__':
    test_stories()
