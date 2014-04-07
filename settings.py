db_host = "localhost"
db_port = 27017
db_name = 'data_bang'
media_path = "/media/document/books"
ignore_seq = {'.git', 'log', 'logs'}
ext_pool = '.pdf'
ignore_hidden = True

try:
    from local_settings import *
except:
    pass
