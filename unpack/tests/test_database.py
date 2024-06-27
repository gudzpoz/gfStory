from gfunpack import database

def test_database():
    db = database.Database('test.db', 'downloader/output')
    db.get_all_images()
    db.close()

if __name__ == '__main__':
    test_database()
