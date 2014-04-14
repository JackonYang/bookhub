# -*- coding: utf-8-*-
import os
import time
import shutil
import pymongo
import lib.util as util
import settings 
param_template = [('REPO_PATH', None),
                  ('host', 'localhost'),
                  ('port', '27017'),
                  ('db_name', 'bookhub'),
                  ]


class MediaRepo:

    def __init__(self):
        params = {k: getattr(settings, k, v) for k, v in param_template}
        # running mode detect by media_path
        self.repo_path = params['REPO_PATH'] or ''
        self.hasRepo = os.path.exists(self.repo_path)

        # connect to db
        self.conn = pymongo.Connection(params['host'], int(params['port']))
        self.db = self.conn[params['db_name']]

    def __del__(self):
        self.conn.disconnect()
        self.conn = None
        self.db = None
        self.repo_path = None
        self.hasRepo = None

    def get_booklist(self):
        return [BookMeta(meta_info) for meta_info in self.db.book.find()]

    def update_meta(self, md5, setter, upsert=False):
        self.db.book.update({'md5': md5}, setter, upsert)

    def getFilePath(self, meta_obj):
        if self.hasRepo:
            paths = [os.path.join(self.repo_path, meta_obj.get_filename())]
        else:
            paths = self.db.history.find_one({'md5': meta_obj.md5},
                                           {'path': 1, '_id': 0}).get('path', [])
        for bookpath in paths:
            if os.path.exists(bookpath):
                return bookpath
        return None  # file not exists

    def add_book(self, src_path, file_meta):
        # rawname, ext in file_meta
        if 'md5' not in file_meta:
            file_meta['md5'] = util.md5_for_file(src_path)

        # book meta info
        file_meta.update({'size_in_bytes': os.path.getsize(src_path)})
        rawname = file_meta.pop("rawname").pop()
        setter = {"$set": file_meta,
                  "$addToSet": {"rawname": rawname},
                  }
        self.update_meta(file_meta['md5'], setter, True)

        # operate history
        self.db.history.update({'md5': file_meta['md5']},
                               {'$addToSet': {'path': src_path,
                                              'scan_time': time.time(),
                                              }},
                               True)  # upsert

        # copy file if has repo
        if self.hasRepo:
            dst_file = os.path.join(self.repo_path,
                                    '%(md5)s%(ext)s' % file_meta)
            if not os.path.exists(dst_file):
                try:
                    shutil.copy(src_path, dst_file)
                except:
                    pass
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

    def getSizeString(self):
        return util.getSizeInNiceString(self.meta.get('size_in_bytes', 0))


    def get_book_language(self):
        return self.meta.get('language', '')


if __name__ == '__main__':
    repo = MediaRepo()
    print repo.get_booklist()[0:2]
