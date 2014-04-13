# -*- coding: utf-8-*-
import hashlib
import subprocess
import os
import sys
if sys.platform.startswith('win'):  # windows
    import win32file
    import win32con


def md5_for_file(filename, block_size=256*128, hr=True):
    """calculate md5 of a file

    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)

    """
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            md5.update(chunk)
    if hr:
        return md5.hexdigest()
    return md5.digest()


def cmd_open_file(filename):
    platform_cmd = {
        'win32': 'start',  # win7 32bit, win7 64bit
        'cygwin': 'start',  # cygwin
        'linux2': 'xdg-open',  # ubuntu 12.04 64bit
        'darwin': 'open',  # Mac
    }
    return '%s %s' % (platform_cmd[sys.platform], filename)


def is_hiden(filepath):
    if sys.platform.startswith('win'):  # windows
        return win32file.GetFileAttributes(filepath)\
            & win32con.FILE_ATTRIBUTE_HIDDEN
    else:  # linux
        return os.path.basename(filepath).startswith('.')


def getSizeInNiceString(sizeInBytes):
    """ Convert the given byteCount into a string like: 9.9bytes/KB/MB/GB

    """
    for (cutoff, label) in [(1024*1024*1024, "GB"),
                            (1024*1024, "MB"),
                            (1024, "KB"),
                            ]:
        if sizeInBytes >= cutoff:
            return "%.1f %s" % (sizeInBytes * 1.0 / cutoff, label)

    if sizeInBytes == 1:
        return "1 byte"
    else:
        bytes = "%.1f" % (sizeInBytes or 0,)
        return (bytes[:-2] if bytes.endswith('.0') else bytes) + ' bytes'
