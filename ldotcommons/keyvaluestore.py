from ldotcommons.sqlalchemy import Base, create_session
from sqlalchemy import Column, String
import json
import pickle
from os import path
from sqlalchemy.orm import exc

_UNDEF = object()


class KeyValueItem(Base):
    __tablename__ = 'item'

    key = Column(String, name='key', primary_key=True,
                 unique=True, nullable=False)
    _value = Column(String, name='value')
    _typ = Column(String(), name='type', default='str', nullable=False)

    _resolved = _UNDEF

    def __init__(self, key, value, typ=None):
        self.key = key
        self._type, self._value = self._native_to_internal(value)
        if typ:
            self._typ = typ

    @property
    def value(self):
        return self._interal_to_native(self._typ, self._value)

    @value.setter
    def value(self, v):
        self._typ, self._value = self._native_to_internal(v)

    @staticmethod
    def _native_to_internal(value):
        if isinstance(value, str):
            typ = 'str'

        elif isinstance(value, bool):
            typ = 'bool'
            value = '1' if value else '0'

        elif isinstance(value, int):
            typ = 'int'
            value = str(value)

        elif isinstance(value, float):
            typ = 'float'
            value = str(value)

        else:
            try:
                value = json.dumps(value)
                typ = 'json'

            except TypeError:
                value = pickle.dumps(value)
                typ = 'pickle'

        return (typ, value)

    @staticmethod
    def _interal_to_native(typ, value):
        if typ == 'bool':
            return (value != '0')

        elif typ == 'int':
            return int(value)

        elif typ == 'float':
            return float(value)

        elif typ == 'str':
            return str(value)

        elif typ == 'json':
            return json.loads(value)

        elif typ == 'pickle':
            return pickle.loads(value)

        raise ValueError((typ, value))


class KeyValueStore:
    def __init__(self, session, separator='.'):
        KeyValueItem.metadata.bind = session.get_bind()
        KeyValueItem.metadata.create_all()
        self._sess = session
        self._query = self._sess.query(KeyValueItem)

    def get(self, k, default=_UNDEF):
        try:
            item = self._query.filter(KeyValueItem.key == k).one()
        except exc.NoResultFound:
            if default is _UNDEF:
                raise KeyError(k)
            else:
                return default

        return item.value

    def set(self, k, v):
        try:
            item = self._query.filter(KeyValueItem.key == k).one()
            item.value = v
        except exc.NoResultFound:
            item = KeyValueItem(key=k, value=v)
            self._sess.add(item)

        self._sess.commit()

    def reset(self, k):
        try:
            item = self.query.filter(KeyValueItem.key == k).one()
        except KeyError:
            pass

        self._sess.delete(item)
        self._sess.commit()

    def children(self, k):
        return map(
            lambda x: x.key,
            self.query.filter(KeyValueItem.key.startswith(k+".")))


class KeyValueStorePath(KeyValueStore):
    def __init__(self, store_path, *args, **kwargs):
        sess = create_session('sqlite:///'+path.realpath(store_path))
        super(KeyValueStorePath, self).__init__(session=sess, **kwargs)


class KeyValueMemory(KeyValueStore):
    def __init__(self, separator='.'):
        sess = create_session('sqlite:///:memory:')
        super(KeyValueMemory, self).__init__(sess, separator=separator)
