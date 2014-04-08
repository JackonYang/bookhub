# -*- coding: utf-8-*-
import sys
from media_repo import install_repo
from settings import ignore_hidden, ignore_seq, ext_pool
from settings import db_host, db_port, db_name, media_path
from lib.scanner import ScanLogCmd, Scanner

repo = install_repo(media_path, db_host, db_port, db_name)
scan_log = ScanLogCmd('INFO')
scan = Scanner(repo.add_book, scan_log, ext_pool=ext_pool,
               ignore_seq=ignore_seq, ignore_hidden=ignore_hidden)

def run(tarpath):
    cnt_found = scan.scan_path(tarpath) or 0
    scan_log.summary(cnt_found, scan.cnt_scanned, tarpath)

if __name__ == '__main__':
    for path in sys.argv[1:]:
        run(path)
