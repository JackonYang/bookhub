# -*- coding: utf-8-*-
# connection
media_path = None
db_host = "localhost"
db_port = 27017
db_name = 'bookhub'

# scan configs
ignore_seq = {'.git', '.svn', 'log', 'logs'}
ext_pool = '.pdf'
ignore_hidden = True

try:
    from local_settings import *
except:
    pass
