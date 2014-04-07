# -*- coding: utf-8-*-
import os
import shutil
import time
from lib.util import md5_for_file
from lib.scanner import Scanner
from settings import media_path, ignore_seq, ext_pool, ignore_hidden
from model import BookMeta


class FileRepo:

    def __init__(self, db, out_scanned=None, out_debug=None):
        self.db = db
        self.out_debug = out_debug
        self.out_scanned = out_scanned
        if not os.path.exists(media_path):
            os.makedirs(media_path)

    def add_books(self, target_path):
        scan = Scanner(self._add_file, self.out_scanned,
                       ignore_seq=ignore_seq,
                       ext_pool=ext_pool,
                       ignore_hidden=ignore_hidden)
        return scan.scan_path(target_path)

    def get_booklist(self):
        return [BookMeta(meta_info) for meta_info in self.db.book.find()]

    def _add_file(self, src_path, file_meta):
        # rawname, ext in file_meta
        if 'md5' not in file_meta:
            file_meta['md5'] = md5_for_file(src_path)

        # copy file to meta_path named md5.ext
        dst_file = os.path.join(media_path, '%(md5)s%(ext)s' % file_meta)
        if not os.path.exists(dst_file):
            shutil.copy(src_path, dst_file)

        file_meta.update({'size_in_bytes': os.path.getsize(src_path),
                          'init_time': time.time()
                          })

        matcher = {'md5': file_meta['md5']}
        setter = {"$set": file_meta,
                  "$addToSet": {"rawname": file_meta.pop("rawname").pop()}
                  }
        self.db.book.update(matcher, setter, True)
        if self.out_debug:
            self.out_debug('add %s, md5: %s' % (src_path, file_meta['md5']))
        return 1

    def get_filepath(self, obj):
        return os.path.join(media_path, obj.get_filename())


if __name__ == "__main__":

    def test_out_scanned(count):
        print '%s files scanned' % count

    def test_out_debug(msg):
        print msg

    from settings import db_host, db_port, db_name
    from lib.mongo_hdlr import MongodbHandler
    mongo = MongodbHandler()
    mongo.connect(db_host, db_port)
    db = mongo.get_db(db_name)

    print ' ------------ Test 1 --------------------'
    repo = FileRepo(db, test_out_scanned, test_out_debug)
    cnt_found, cnt_scanned = repo.add_books(u'/media/document/books')
    print '%s path/files scanned, %s found' % (cnt_scanned, cnt_found or 0)

    for obj in repo.get_booklist():
        print repo.get_filepath(obj)
