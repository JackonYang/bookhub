# -*- coding: utf-8-*-
import os
import time
import shutil
import pymongo
import lib.util as util


repo = None


def install_repo(*args, **kwargs):
    global repo
    if repo is None:
        repo = MediaRepo(*args, **kwargs)
    return repo


class MediaRepo:

    def __init__(self, repo_path,
                 host='localhost', port=27017, db_name='data_bang'):
        self.conn = pymongo.Connection(host, int(port))
        self.db = self.conn[db_name]
        self.repo_path = repo_path

    def __del__(self):
        self.conn.disconnect()
        self.conn = None

    def get_booklist(self):
        return [BookMeta(meta_info) for meta_info in self.db.book.find()]

    def update_meta(self, md5, setter, upsert=False):
        self.db.book.update({'md5': md5}, setter, upsert)

    def open_book(self, meta_obj):
        util.open_file(os.path.join(self.repo_path, meta_obj.get_filename()))

    def add_book(self, src_path, file_meta):
        # rawname, ext in file_meta
        if 'md5' not in file_meta:
            file_meta['md5'] = util.md5_for_file(src_path)

        # copy file to meta_path named md5.ext
        dst_file = os.path.join(self.repo_path, '%(md5)s%(ext)s' % file_meta)
        if not os.path.exists(dst_file):
            try:
                shutil.copy(src_path, dst_file)
            except:
                pass

        file_meta.update({'size_in_bytes': os.path.getsize(src_path),
                          'init_time': time.time()
                          })

        setter = {"$set": file_meta,
                  "$addToSet": {"rawname": file_meta.pop("rawname").pop()}
                  }
        self.update_meta(file_meta['md5'], setter, True)
        return 1


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
    print repo.get_booklist()[0:1]
    test_file = os.listdir(media_path)[0]
    rawname, ext = os.path.splitext(os.path.basename(test_file))
    file_meta = {'rawname': [rawname],
                 'ext': ext
                 }
    print repo.add_book(os.path.join(media_path, test_file), file_meta)
