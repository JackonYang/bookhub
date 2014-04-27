# -*- coding: utf-8-*-
# connection
REPO_PATH = None
host = "localhost"
port = 27017
db_name = 'bookhub'

# scan configs
ignore_seq = {'.git', '.svn', 'log', 'logs'}
ext_pool = '.pdf'
ignore_hidden = True

try:
    from local_settings import *
except:
    pass
