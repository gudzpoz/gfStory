from gfunpack import chapters
from gfunpack import stories


def test_stories():
    ss = stories.Stories('downloader/output', 'stories')
    ss.save()
    chapters.Chapters(ss).save()
    print(sorted(ss.transpiler.tag_collection))
    

if __name__ == '__main__':
    test_stories()
