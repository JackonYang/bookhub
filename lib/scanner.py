# -*- coding: utf-8-*-
import os
from util import is_hiden


class Scanner():

    def __init__(self, file_hdlr, out_scanned=None, ignore_seq=None,
                 ext_pool='.pdf', ignore_hidden=True):
        self.stop_flag = False
        self.ignore_seq = ignore_seq or set()
        self.ignore_hidden = ignore_hidden
        self.ext_pool = ext_pool

        self.scanned = 0
        self.out_scanned = out_scanned
        self.file_hdlr = file_hdlr

    def stop_scan(self):
        self.stop_flag = True

    def scan_path(self, src_path):
        """scan path to detect target files

        @src_path: unicode encoding is required"""
        return (self._scan_path(src_path), self.scanned)

    def _scan_path(self, src_path):
        if not os.path.exists(src_path):  # not exists
            return None

        if os.path.isfile(src_path):  # file
            rawname, ext = os.path.splitext(os.path.basename(src_path))
            if not ext or ext not in self.ext_pool:  # file extension check
                return 0
            file_meta = {'rawname': [rawname],
                         'ext': ext
                         }
            return self.file_hdlr(src_path, file_meta) or 0
        else:  # dir
            if self.stop_flag:
                return 0
            added = 0
            # ignore log/.git etc
            tar_path = set(os.listdir(src_path)) - self.ignore_seq
            self.scanned += len(tar_path)
            if self.out_scanned:
                self.out_scanned(self.scanned)
            for rel_path in tar_path:
                abs_path = os.path.join(src_path, rel_path)
                if self.ignore_hidden and is_hiden(abs_path):
                    continue  # ignore hidden
                else:
                    added += self._scan_path(abs_path) or 0
            return added


if __name__ == "__main__":

    def test_file_hdlr(src_path, file_meta):
        print 'find file: %s' % src_path
        return 1

    def test_out_scanned(count):
        print '%s files scanned' % count

    print ' ------------ Test 1 --------------------'
    scan = Scanner(test_file_hdlr, test_out_scanned,
                    ignore_seq={'log', '.git'}, ext_pool='.py')
    cnt_found, cnt_scanned = scan.scan_path(u'..')
    print '%s path/files scanned, %s found' % (cnt_scanned, cnt_found or 0)

    print ' ------------ Test 2 --------------------'
    scan = Scanner(test_file_hdlr, ext_pool='.py')
    cnt_found, cnt_scanned = scan.scan_path(u'.')
    print '%s path/files scanned, %s found' % (cnt_scanned, cnt_found or 0)
