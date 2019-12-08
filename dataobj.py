# -*- coding: utf-8 -*-
import sqlite3


class dataobj(object):
    """
    연습삼아 만들어본 ORM 객체 입니다.
    데이터베이스 테이블과 1:1 연결되는 기본 객체 입니다.
    TABLE_FIELDS 에 데이터베이스 필드 리스트를 초기화 해주면 dataobjmanager에서
    query_obj, query_obj_one메서드를 이용해 데이터를 자동으로 채울 수 있습니다.
    """
    TABLE_FIELDS = []

    def __repr__(self):
        return {k: getattr(self, k) for k in self.TABLE_FIELDS}.__repr__()


class dataobjmanager(object):
    """
    dataobj를 제어하는 매니저 객체 입니다.
    """
    def __init__(self, dbname):
        self.db = sqlite3.connect("%s.db" % (dbname,), timeout=5, check_same_thread=False)
        self.tables = {}

    def get_conn(self):
        """
        데이터베이스 커넥션 풀에서 커넥션을 하나 받아옵니다. 보통 with절과 함께 사용합니다.
        """
        return self.db

    def set_table(self, db, tablename, tabledef, exception_column_list=[]):
        """
        데이터베이스에 테이블을 생성하고 매니저에서 사용할 수 있도록 초기화 합니다.
        """
        after_queries = [" ".join(x.split("!")[1:]) for x in tabledef if x.startswith("!")]
        create_query = "CREATE TABLE IF NOT EXISTS {0} (\n{1}\n); ".format(tablename, ",\n".join(["\t%s"%f for f in tabledef if not f.startswith("!")]))
        if __debug__:
            print create_query
            print after_queries
        rs = self.query(db, "SELECT name FROM sqlite_temp_master WHERE type='table' and name=?;", (tablename,))
        if not rs:
            self.query(db, create_query)
            for q in after_queries:
                self.query(db, q)

        cur = db.execute("SELECT * FROM {0} LIMIT 0;".format(tablename))
        self.tables[tablename] = [x[0] for x in cur.description if x [0] not in exception_column_list]

    def query(self, db, q, a=()):
        """
        쿼리를 실행하고 결과를 레코드셋으로 반환 합니다.
        """
        c = db.execute(q, a)
        return c.fetchall()

    def query_obj(self, db, obj_type, q, a=()):
        """
        쿼리를 실행하고 해당 결과를 obj_type의 형식으로 변환하여 결과 리스트를 반환 합니다.
        데이터가 없는 경우 빈 리스트를 반환 합니다.
        """
        if not issubclass(obj_type, dataobj):
            raise Exception("basemanager::query_obj %s is not subclass of baseobj", obj_type)

        obj_list = []

        cur = db.execute(q, a)
        column_list = list(map(lambda x: x[0], cur.description))

        rs = cur.fetchall()
        for item in rs:
            obj =  object.__new__(obj_type)
            for n, i in enumerate(item):
                setattr(obj, column_list[n], i)
            obj_list.append(obj)

        return obj_list

    def query_obj_one(self, db, obj_type, q, a=()):
        """
        쿼리를 실행하고 첫 번째 결과 레코드를 obj_type 형식으로 변환하여 obj_type의 인스턴스를 반환 합니다.
        데이터가 없는 경우 None을 반환 합니다.
        """
        obj_list = self.query_obj(db, obj_type, q, a)
        if obj_list and len(obj_list) > 0:
            return obj_list[0]
        else:
            return None

    def drop_table(self, tablename):
        """
        테이블을 삭제 합니다. 데이터도 함께 삭제되니 테스트 목적에만 사용 가능 합니다.
        """
        with self.db.get_conn() as db:
            rs = self.query(db, "SELECT name FROM sqlite_temp_master WHERE type='table' and name=?;", (tablename,))
            if rs:
                db.execute("DROP TABLE ?;", (tablename,))
