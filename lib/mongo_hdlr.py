# -*- coding: utf-8 -*-
#!/usr/bin/python
import pymongo


class MongodbHandler():

    def __init__(self):
        self.db = None

    def __del__(self):
        self.disconnect()

    def connect(self, host='localhost', port=27017):
        try:
            self.db = pymongo.Connection(host, int(port))
        except:
            return False
        else:
            return self._checkConnection()

    def disconnect(self):
        if self._checkConnection():
            self.db.disconnect()
            self.db = False

    def _checkConnection(self):
        if isinstance(self.db, pymongo.connection.Connection):
            return True
        else:
            return False

if __name__ == '__main__':
    db = MongodbHandler()
    print 'before connect, Connectted: %s' % db._checkConnection()
    db.connect()
    print 'before disconnect, Connectted: %s' % db._checkConnection()
    db.disconnect()
    print 'after disconnect, Connectted: %s' % db._checkConnection()
