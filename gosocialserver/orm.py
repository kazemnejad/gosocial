from abc import ABC, abstractmethod

import datetime
from mysql.connector import MySQLConnection

from gosocialserver import config


def get_value_str(value):
    if not value:
        return "NULL"

    return '"%s"' % value if type(value) is str or isinstance(value, datetime.datetime) else str(value)


class Database:
    _db = None

    @staticmethod
    def session():
        if not Database._db:
            Database._init()

        return Database._db

    @staticmethod
    def _init():
        Database._db = MySQLConnection(
            host="localhost",
            user=config.db['user'],
            password=config.db['password'],
            database=config.db['database'],
            autocommit=True
        )


class Query:
    def __init__(self, raw_sql):
        print("query:", raw_sql)
        self.sql = raw_sql
        self.model_class = None

    def with_model(self, model):
        self.model_class = model
        return self

    def _execute(self):
        cursor = Database.session().cursor()
        cursor.execute(self.sql)
        return cursor

    def execute(self):
        return self._execute()

    def first(self):
        cursor = self._execute()
        data = cursor.fetchone()
        cursor.close()
        return self.model_class(data) if data else None

    def all(self):
        cursor = self._execute()
        for row in cursor.fetchall():
            yield self.model_class(row)

        cursor.close()


class QueryBuilder(ABC):
    @abstractmethod
    def to_query(self):
        pass


class Operator:
    EQUAL = "="
    NOT_EQUAL = "!="
    BIGGER = ">"
    SMALLER = "<"
    BIGGER_OR_EQUAL = BIGGER + EQUAL
    SMALLER_OR_EQUAL = SMALLER + EQUAL


class Expression:
    def __init__(self, field):
        self.field = field
        self.operator = None
        self.value = None

    def equal(self, value):
        self.operator = Operator.EQUAL
        self.value = value

        return self

    def not_equal(self, value):
        self.operator = Operator.NOT_EQUAL
        self.value = value

        return self

    def biggerThan(self, value):
        self.operator = Operator.BIGGER
        self.value = value

        return self

    def smallerThan(self, value):
        self.operator = Operator.SMALLER
        self.value = value

        return self

    def biggerOrEqualThan(self, value):
        self.operator = Operator.BIGGER_OR_EQUAL
        self.value = value

        return self

    def smallerOrEqualThan(self, value):
        self.operator = Operator.SMALLER_OR_EQUAL
        self.value = value

        return self


column = Expression


class Whereble(ABC):
    def __init__(self):
        self.where = ""
        self.is_where_written = False

    def And(self):
        assert self.is_where_written
        self.where += " "
        self.where += "AND"

        return self

    def Or(self):
        assert self.is_where_written
        self.where += " "
        self.where += "OR"

        return self

    def filter(self, expression):
        if not self.is_where_written:
            self.where = "where"
            self.is_where_written = True

        self.where += " "
        self.where += "`" + expression.field + "`"
        self.where += " "
        self.where += expression.operator
        self.where += " "
        self.where += get_value_str(expression.value)

        return self


class Orderable(ABC):
    def __init__(self):
        self.order = ""
        self.is_order_written = False

    def by(self, field):
        if not self.is_order_written:
            self.order += "order by"
            self.is_order_written = True

        self.order += " "
        self.order += "`" + field + "`"

        return self

    def desc(self):
        assert self.is_order_written
        self.order += " DESC"

        return self

    def asc(self):
        assert self.is_order_written
        self.order += " ASC"

        return self


class Select(QueryBuilder, Whereble, Orderable):
    def __init__(self):
        QueryBuilder.__init__(self)
        Whereble.__init__(self)
        Orderable.__init__(self)

        self.sql = ""
        self.table = ""

        self.is_fields_written = False
        self.is_from_written = False
        self.is_select_written = False

    def to_query(self):
        return Query(self.sql + " " + self.where + " " + self.order)

    def fields(self, columns):
        assert not self.is_select_written
        assert not self.is_fields_written
        assert not self.is_from_written
        assert not self.is_where_written

        self.sql += "select "
        if columns:
            for i in range(len(columns)):
                column = columns[i]
                self.sql += "`" + column + "`"

                if i != len(columns) - 1:
                    self.sql += ","
        else:
            self.sql += "*"

        self.is_select_written = True
        self.is_fields_written = True

        return self

    def star(self):
        return self.fields(None)

    def From(self, table_name):
        assert self.is_select_written
        assert self.is_fields_written
        self.table = table_name

        self.sql += " from %s" % table_name

        return self


class Update(QueryBuilder, Whereble):
    def __init__(self, table_name):
        QueryBuilder.__init__(self)
        Whereble.__init__(self)

        self.table = table_name
        self.update = ""

        self.is_set_written = False
        self.is_update_written = False

    def to_query(self):
        return Query(self.update + " " + self.where)

    def set(self, kwargs):
        assert not self.is_update_written

        self.update += "update " + self.table
        self.is_update_written = True

        self.update += " set"

        counter = 0
        for key, value in kwargs.items():
            self.update += " `" + key + "`"
            self.update += " = "
            self.update += get_value_str(value)

            if counter != len(kwargs) - 1:
                self.update += ","

            counter += 1

        return self


class Insert(QueryBuilder):
    def __init__(self):
        QueryBuilder.__init__(self)

        self.table = ""
        self.insert = ""

        self.is_insert_written = False
        self.is_values_written = False

    def to_query(self):
        return Query(self.insert)

    def into(self, table_name):
        assert not self.is_insert_written
        assert not self.is_values_written

        self.table = table_name
        self.insert += "insert into %s" % table_name

        self.is_insert_written = True
        return self

    def values(self, kwargs):
        assert self.is_insert_written
        assert not self.is_values_written

        columns = "("
        values = "("

        counter = 0
        for key, value in kwargs.items():
            columns += " `%s`" % key
            values += ' %s' % get_value_str(value)

            if counter != len(kwargs) - 1:
                columns += ","
                values += ","

            counter += 1

        columns += ")"
        values += ")"

        self.insert += " " + columns + " values " + values

        self.is_values_written = True
        return self


class Model(ABC):
    table_name = ""

    def __init__(self):
        self.data = tuple()
        self.saved_data = {}

    @property
    def id(self):
        return self._get_property(0)

    @id.setter
    def id(self, value):
        self.saved_data[0] = value

    @abstractmethod
    def _get_property_dict(self):
        pass

    def _save(self, table):
        cur = Insert().into(table).values(self._get_property_dict()).to_query().execute()
        cur.close()
        return cur.getlastrowid()

    def _save_or_update(self, table, clazz, ):
        obj = None
        if self.id:
            obj = Select().fields(["id"]).From(table) \
                .filter(column("id").equal(self.id)) \
                .to_query() \
                .with_model(clazz).first()

        if not obj or not id:
            cur = Insert().into(table).values(self._get_property_dict()).to_query().execute()
            row_id = cur.getlastrowid()
        else:
            cur = Update(table) \
                .set(self._get_property_dict()) \
                .filter(column("id").equal(self.id)) \
                .to_query().execute()
            row_id = self.id

        cur.close()
        return row_id

    def _get_property(self, index):
        in_saved_data = self.saved_data.get(index)
        if index in self.saved_data:
            return in_saved_data

        try:
            return self.data[index]
        except IndexError as error:
            return None

    @staticmethod
    def _query_all(table, clazz):
        return Select() \
            .star() \
            .From(table) \
            .to_query() \
            .with_model(clazz) \
            .all()

    @staticmethod
    def _query_by_id(table, clazz, id):
        return Select() \
            .star() \
            .From(table) \
            .filter(column("id").equal(id)) \
            .to_query() \
            .with_model(clazz) \
            .first()

    @staticmethod
    @abstractmethod
    def all():
        pass

    @staticmethod
    @abstractmethod
    def get_by_id(id):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def save_or_update(self):
        pass
