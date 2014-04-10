# -*- coding: utf-8-*-
import os
import time
import shutil
import pymongo
import lib.util as util
import settings

param_template = [('media_path', None),
                  ('host', 'localhost'),
                  ('port', '27017'),
                  ('db_name', 'bookhub'),
                  ]


class MediaRepo:

    def __init__(self):
        params = {k: getattr(settings, k, v) for k, v in param_template}
        # running mode detect by media_path
        self.repo_path = params['media_path']

        # connect to db
        self.conn = pymongo.Connection(params['host'], int(params['port']))
        self.db = self.conn[params['db_name']]

    def __del__(self):
        self.conn.disconnect()
        self.conn = None
        self.db = None
        self.repo_path = None

    def get_booklist(self):
        return [BookMeta(meta_info) for meta_info in self.db.book.find()]

    def update_meta(self, md5, setter, upsert=False):
        self.db.book.update({'md5': md5}, setter, upsert)

    def open_book(self, meta_obj):
        if self.repo_path:
            bookpath = os.path.join(self.repo_path, meta_obj.get_filename())
        else:
            res = self.db.bookpath.find_one({'md5': meta_obj.md5},
                                            {'orig_path': 1, '_id': 0})
            bookpath = res['orig_path'].pop()
            print bookpath
        util.open_file(bookpath)

    def add_book(self, src_path, file_meta):
        # rawname, ext in file_meta
        if 'md5' not in file_meta:
            file_meta['md5'] = util.md5_for_file(src_path)

        if self.repo_path:
            # copy file to meta_path named md5.ext
            dst_file = os.path.join(self.repo_path,
                                    '%(md5)s%(ext)s' % file_meta)
            if not os.path.exists(dst_file):
                try:
                    shutil.copy(src_path, dst_file)
                except:
                    pass
        else:
            self.db.bookpath.update({'md5': file_meta['md5']},
                                    {'$addToSet': {'orig_path': src_path}},
                                    True)

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
        MediaRepo().update_meta(self.md5, {"$set": {"dispname": dispname}})

    def get_sizeInMb(self):
        return self.meta.get('size_in_bytes', 0) / (1024.0*1024.0)

    def get_book_language(self):
        return self.meta.get('language', '')


if __name__ == '__main__':
    repo = MediaRepo()
    print repo.get_booklist()[0:2]
