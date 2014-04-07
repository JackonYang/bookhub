# -*- coding: utf-8-*-
from lib.scanner import Scanner
from lib.file_repo import FileRepo
from lib.mongo_hdlr import MongodbHandler
from settings import db_host, db_port, db_name, media_path, ignore_seq, ext_pool, ignore_hidden


class BookScan(Scanner):

    def __init__(self, out_scanned, out_debug):
        mongo = MongodbHandler()
        mongo.connect(db_host, db_port)
        db = mongo.get_db(db_name)
        file_hdlr = FileRepo(media_path, db, out_debug).add_file
        Scanner.__init__(self, file_hdlr, out_scanned,
                         ignore_seq=ignore_seq,
                         ext_pool=ext_pool,
                         ignore_hidden=ignore_hidden)


if __name__ == "__main__":

    def test_out_scanned(count):
        print '%s files scanned' % count

    def test_out_debug(msg):
        print msg

    print ' ------------ Test 1 --------------------'
    scan = BookScan(test_out_scanned, test_out_debug)
    cnt_found, cnt_scanned = scan.scan_path(u'/media/document/books')
    print '%s path/files scanned, %s found' % (cnt_scanned, cnt_found or 0)
