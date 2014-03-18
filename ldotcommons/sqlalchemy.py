import re
import warnings

import sqlalchemy as sa
from sqlalchemy import orm, event
from sqlalchemy.sql import sqltypes
from sqlalchemy.ext import declarative

from ldotcommons import utils


Base = declarative.declarative_base()


def _re_fn(regexp, other):
    return re.search(regexp, other, re.IGNORECASE) is not None


def create_engine(uri='sqlite:///:memory:', echo=False, dburi=None):
    if dburi:
        warnings.warn('Usage of dburi is deprecated, use uri instead')
        uri = dburi

    engine = sa.create_engine(uri, echo=echo)
    Base.metadata.create_all(engine)
    return engine


def create_session(uri=None, engine=None, echo=False, dburi=None):
    if not engine:
        engine = create_engine(uri=uri, echo=echo, dburi=dburi)

    session = orm.scoped_session(orm.sessionmaker(bind=engine))

    @event.listens_for(engine, "begin")
    def do_begin(conn):
        conn.connection.create_function('regexp', 2, _re_fn)

    return session


class Filter:
    def __init__(self, session, mapping):
        self._sess = session
        self._mapping = mapping
        self._ops = {}

        columns = self._mapping.__table__.columns
        for (colname, column) in columns.items():
            columntype = column.type
            if isinstance(columntype, sqltypes.String):
                self._ops[(colname, None)] = self.by_string
                self._ops[(colname, 'like')] = self.by_string_like
                self._ops[(colname, 'regexp')] = self.by_string_regexp

            if isinstance(columntype, sqltypes.Integer):
                self._ops[(colname, 'min')] = self.by_amount_min
                self._ops[(colname, 'max')] = self.by_amount_max

    def _get_base_query(self):
        return self._sess.query(self._mapping)

    def _get_torrent_attr(self, key):
        try:
            return getattr(self._mapping, key, None)
        except AttributeError:
            pass

        raise Exception('Invalid key: {}'.format(key))

    def _by(self, prop, expr, q=None):
        if '_' in prop:
            key = '_'.join(prop.split('_')[:-1])
            mod = prop.split('_')[-1]
        else:
            key = prop
            mod = None

        try:
            return self._ops[(key, mod)](key, expr, q=q)
        except KeyError:
            pass

        raise Exception('Unknow operator {}'.format(prop))

    def by(self, **expressions):
        q = self._get_base_query()
        for (prop, expr) in expressions.items():
            q = self._by(prop, expr, q=q)

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
