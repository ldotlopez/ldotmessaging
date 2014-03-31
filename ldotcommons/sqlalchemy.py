import json
import re
import warnings

import sqlalchemy as sa
from sqlalchemy import orm, event
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


def query_from_params(conn, mapping, **params):

    # This code can be used for add type-safety to this function
    #from sqlalchemy.sql import sqltypes
    #columns = self._mapping.__table__.columns
    #for (colname, column) in columns.items():
    #    columntype = column.type
    #    if isinstance(columntype, sqltypes.String):
    #        self._ops[(colname, None)] = self.by_string
    #        self._ops[(colname, 'like')] = self.by_string_like
    #        self._ops[(colname, 'regexp')] = self.by_string_regexp
    #
    #    if isinstance(columntype, sqltypes.Integer):
    #        self._ops[(colname, 'min')] = self.by_amount_min
    #        self._ops[(colname, 'max')] = self.by_amount_max

    q = conn.query(mapping)

    for (prop, value) in params.items():
        if '_' in prop:
            key = '_'.join(prop.split('_')[:-1])
            mod = prop.split('_')[-1]
        else:
            key = prop
            mod = None

        attr = getattr(mapping, key, None)

        if mod == 'like':
            q = q.filter(attr.like(value))

        elif mod == 'regexp':
            q = q.filter(attr.op('regexp')(value))

        elif mod == 'min':
            value = utils.parse_size(value)
            q = q.filter(attr >= value)

        elif mod == 'max':
            value = utils.parse_size(value)
            q = q.filter(attr <= value)

        else:
            q = q.filter(attr == value)

    return q


def load_fixtures_file(conn, fixtures_file, loader_func):
    with open(fixtures_file) as fh:
        fixtures = json.load(fh)
        return load_fixtures(conn, fixtures, loader_func)


def load_fixtures(conn, fixtures, loader_func):
    conn.add_all([loader_func(x) for x in fixtures])


def glob_to_like(x):
    for (g, l) in (('*', '%'), ('.', '_')):
        x = x.replace(g, l)
    return x
