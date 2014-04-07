# -*- coding: utf-8-*-
import os
import shutil
import time
from util import md5_for_file


class FileRepo:

    def __init__(self, media_path, db, out_debug=None):
        self.media_path = media_path
        self.db = db
        self.out_debug = out_debug
        if not os.path.exists(self.media_path):
            os.makedirs(self.media_path)

    def add_file(self, src_path, file_meta):
        # rawname, ext in file_meta
        if 'md5' not in file_meta:
            file_meta['md5'] = md5_for_file(src_path)

        # copy file to meta_path named md5.ext
        dst_file = os.path.join(self.media_path, '%(md5)s%(ext)s' % file_meta)
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
