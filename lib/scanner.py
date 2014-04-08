# -*- coding: utf-8-*-
import os
import util as util


class ScanLogCmd:

    def __init__(self, lvl='INFO'):
        self.lvl = lvl.upper()

    def found(self, filepath, md5):
        if self.lvl == 'INFO' or self.lvl == 'DEBUG':
            print 'add %s, md5: %s' % (filepath, md5)

    def scanned(self, cnt):
        if self.lvl == 'DEBUG':
            print '%s files scanned' % cnt

    def summary(self, cnt_found, cnt_scanned, path):
        if self.lvl == 'INFO' or self.lvl == 'DEBUG':
            print '%s/%s (found/scanned) in path %s' % (cnt_found, cnt_scanned, os.path.abspath(path))


class Scanner():

    def __init__(self, file_hdlr, scan_log=None, ext_pool='.pdf',
                 ignore_seq=None, ignore_hidden=True):
        self.ignore_seq = ignore_seq or set()
        self.ignore_hidden = ignore_hidden
        self.ext_pool = ext_pool

        self.cnt_scanned = 0
        self.scan_log = scan_log
        self.file_hdlr = file_hdlr

    def scan_path(self, src_path):
        """scan path to detect target files

        @src_path: unicode encoding is required"""
        if not os.path.exists(src_path):  # not exists
            return None

        if os.path.isfile(src_path):  # file
            rawname, ext = os.path.splitext(os.path.basename(src_path))
            if not ext or ext not in self.ext_pool:  # file extension check
                return 0
            file_meta = {'rawname': [rawname],
                         'ext': ext,
                         'md5': util.md5_for_file(src_path),
                         }
            self.scan_log.found(src_path, file_meta['md5'])
            return self.file_hdlr(src_path, file_meta) or 0
        else:  # dir
            added = 0
            # ignore log/.git etc
            tar_path = set(os.listdir(src_path)) - self.ignore_seq
            self.cnt_scanned += len(tar_path)
            self.scan_log.scanned(self.cnt_scanned)
            for rel_path in tar_path:
                abs_path = os.path.join(src_path, rel_path)
                if self.ignore_hidden and util.is_hiden(abs_path):
                    continue  # ignore hidden
                else:
                    added += self.scan_path(abs_path) or 0
            return added


if __name__ == "__main__":

    def test_file_hdlr(src_path, file_meta):
        print 'find file: %s' % src_path
        return 1

    scan_log = ScanLogCmd('INFO')
    scan = Scanner(test_file_hdlr, scan_log,
                    ignore_seq={'log', '.git'}, ext_pool='.py')
    cnt_found = scan.scan_path(u'.') or 0
    scan_log.summary(cnt_found, scan.cnt_scanned, u'.')
