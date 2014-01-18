#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import sqlite3
import hashlib

class Database:
    def __init__(self, datafile):
        self.db = sqlite3.connect(datafile)
        self.cur = self.db.cursor()

    def __del__(self):
        self.close()

    def commit(self):
        self.db.commit()

    def close(self):
        if hasattr(self,'db'):
            self.db.close()

    def schema_db(self,schema):
        with open(schema,'r') as s:
            sql = s.read()
            self.cur.executescript(sql)
        self.commit()

    def update(self,*data):
        Homepage = data[0]
        self.cur.execute(u'select Times from albums where Homepage=?',[Homepage])
        times = 1
        try:
            times = self.cur.fetchone()[0]
            times+=1
        except Exception, e:
            pass
        self.cur.execute(u'REPLACE INTO albums (Homepage,Title,Cover,HasPics,GetPics,ImgUrls,Times)\
         VALUES (?,?,?,?,?,?,?)',
         data+tuple([times])
         )
        self.commit()


def store_img(path,img,ext):
    md5 = hashlib.md5(img).hexdigest()
    file_name = '%s.%s' %(md5,ext)
    f= open('%s/%s' %(path,file_name),'wb')
    f.write(img)
    f.close()
    return file_name

def init_db():
    DATABASE= 'DATA/albums.db'
    INIT = 'DATA/schema.sql'
    db = Database(DATABASE)
    db.schema_db(INIT)    
        
if __name__ == '__main__':
    init_db()

