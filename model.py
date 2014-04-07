# -*- coding: utf-8-*-
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
        db.book.update({'md5': self.md5}, {"$set": {"dispname": dispname}})

    def get_sizeInMb(self):
        return self.meta.get('size_in_bytes', 0) / (1024.0*1024.0)

    def get_book_language(self):
        return self.meta.get('language', '')
