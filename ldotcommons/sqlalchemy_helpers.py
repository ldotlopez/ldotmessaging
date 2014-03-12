import re

import sqlalchemy as sa
from sqlalchemy import orm, event
from sqlalchemy.sql import sqltypes
from sqlalchemy.ext import declarative

from ldotcommons import utils


Base = declarative.declarative_base()


def create_engine(dbpath='sqlite:///:memory:', echo=False):
    engine = sa.create_engine(dbpath, echo=echo)
    Base.metadata.create_all(engine)
    return engine


def create_session(dbpath=None, engine=None, echo=False):
    if not engine:
        engine = create_engine(dbpath, echo)
    Session = orm.sessionmaker(bind=engine)
    return Session()


class Filter:
    def __init__(self, dbpath, mapping):
        self.engine = create_engine(dbpath='sqlite:///'+dbpath)
        self.sess = orm.scoped_session(orm.sessionmaker(bind=self.engine))
        self.mapping = mapping
        self._ops = {}

        columns = self.mapping.__table__.columns
        for (colname, column) in columns.items():
            columntype = column.type
            if isinstance(columntype, sqltypes.String):
                self._ops[(colname, None)] = self.by_string
                self._ops[(colname, 'like')] = self.by_string_like
                self._ops[(colname, 'regexp')] = self.by_string_regexp

            if isinstance(columntype, sqltypes.Integer):
                self._ops[(colname, 'min')] = self.by_amount_min
                self._ops[(colname, 'max')] = self.by_amount_max

        @event.listens_for(self.engine, "begin")
        def do_begin(conn):
            conn.connection.create_function('regexp', 2, Filter._re_fn)

    @staticmethod
    def _re_fn(regexp, other):
        return re.search(regexp, other, re.IGNORECASE) is not None

    def _get_base_query(self):
        return self.sess.query(self.mapping)

    def _get_torrent_attr(self, key):
        try:
            return getattr(self.mapping, key, None)
        except AttributeError:
            pass

        raise Exception('Invalid key: {}'.format(key))

    def by(self, prop, expr, q=None):
        if '-' in prop:
            key = '-'.join(prop.split('-')[:-1])
            mod = prop.split('-')[-1]
        else:
            key = prop
            mod = None

        try:
            return self._ops[(key, mod)](key, expr, q=q)
        except KeyError:
            pass

        raise Exception('Unknow operator {}'.format(prop))

    def composed(self, *expressions, q=None):
        for (prop, expr) in expressions:
            q = self.by(prop, expr, q=q)

        return q

    def by_string(self, key, value, q=None):
        if q is None:
            q = self._get_base_query()

        attr = self._get_torrent_attr(key)

        return q.filter(attr == value)

    def by_string_like(self, key, value, q=None):
        if q is None:
            q = self._get_base_query()

        attr = self._get_torrent_attr(key)
        value = value.replace('*', '%').replace('.', '_')

        return q.filter(attr.like(value))

    def by_string_regexp(self, key, regexp, q=None):
        if q is None:
            q = self._get_base_query()

        attr = self._get_torrent_attr(key)
        return q.filter(attr.op('regexp')(regexp))

    def by_amount_min(self, key, value, q=None):
        if q is None:
            q = self._get_base_query()

        attr = self._get_torrent_attr(key)
        if not isinstance(value, int):
            amount = utils.parse_size(value)

        return q.filter(attr >= amount)

    def by_amount_max(self, key, value, q=None):
        if q is None:
            q = self._get_base_query()

        attr = self._get_torrent_attr(key)
        if not isinstance(value, int):
            amount = utils.parse_size(value)

        return q.filter(attr <= amount)
