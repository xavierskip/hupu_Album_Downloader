import pymysql.cursors

class Database:
    def __init__(self,host,port,user,passwd,db,charset="utf8"):
        self.conn = pymysql.connect(
            host = host,
            port = port,
            user = user,
            passwd = passwd,
            db = db,
            charset=charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cur = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def init_db():
    from config import *
    conn = pymysql.connect(
        host = HOST,
        port = PORT,
        user = DBUSER,
        passwd = DBPASSWD
    )
    try:
        with conn.cursor() as cursor:
            with open("web/schema.sql") as sql:
                for line in sql.read().split(';\n'):
                    cursor.execute(line)
        conn.commit()
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()