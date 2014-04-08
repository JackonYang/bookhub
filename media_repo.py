# -*- coding: utf-8-*-
import pymongo


repo = None

def install_repo(*args, **kwargs):
    global repo
    if repo is None:
        repo = MediaRepo(*args, **kwargs)

class MediaRepo:

    def __init__(self, repo_path, host='localhost', port=27017, db_name='data_bang'):
        self.conn = pymongo.Connection(host, int(port))
        self.db = self.conn[db_name]

    def __del__(self):
        self.conn.disconnect()
        self.conn = None

    def get_booklist(self):
        return [BookMeta(meta_info) for meta_info in self.db.book.find()]

    def update_meta(self, md5, setter):
        self.db.book.update({'md5': md5}, setter)


class BookMeta:
    """Meta info of a single book

    """

    def __init__(self, meta):
        self.meta = meta
        self.md5 = meta['md5']
        self.ext = meta['ext']

    def get_filename(self):
        return self.md5+self.ext

    def get_dispname(self):
        return self.meta.get('dispname', ','.join(self.meta['rawname']))

    def set_dispname(self, dispname):
        self.meta['dispname'] = dispname
        repo.update_meta(self.md5, {"$set": {"dispname": dispname}})

    def get_sizeInMb(self):
        return self.meta.get('size_in_bytes', 0) / (1024.0*1024.0)

    def get_book_language(self):
        return self.meta.get('language', '')


if __name__ == '__main__':
    media_path = "/media/document/books"
    install_repo(media_path)
    print repo.get_booklist()
