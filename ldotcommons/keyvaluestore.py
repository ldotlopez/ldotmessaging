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
    value_ = Column(String, name='value')
    typ = Column(String(), name='type', default='string', nullable=False)
    _resolved = _UNDEF

    def __init__(self, key, value, typ=None):
        if isinstance(value, bool):
            typ = 'bool'
        elif isinstance(value, int):
            typ = 'int'
        elif isinstance(value, float):
            typ = 'float'
        elif isinstance(value, str):
            typ = 'str'
        else:
            try:
                value = json.dumps(value)
                typ = 'json'

            except TypeError:
                value = pickle.dumps(value)
                typ = 'pickle'

        self.key = key
        self.value_ = value
        self.typ = typ

    @property
    def value(self):
        if self._resolved == _UNDEF:
            if self.typ == 'bool':
                self._resolved = (self.value_ == '1')

            elif self.typ == 'int':
                self._resolved = int(self.value_)

            elif self.typ == 'float':
                self._resolved = float(self.value_)

            elif self.typ == 'str':
                self._resolved = str(self.value_)

            elif self.typ == 'json':
                self._resolved = json.loads(self.value_)

            elif self.typ == 'pickle':
                self._resolved = pickle.loads(self.value_)

        return self._resolved

    @value.setter
    def value(self, v):
        self.value_ = v


class KeyValueStore:
    def __init__(self, store_path, separator='.'):

        self._sess = create_session('sqlite:///'+path.realpath(store_path))
        self.query = self._sess.query(KeyValueItem)

    def get(self, k, default=_UNDEF):
        try:
            item = self.query.filter(KeyValueItem.key == k).one()
        except exc.NoResultFound:
            if default is _UNDEF:
                raise KeyError(k)
            else:
                return default

        return item.value

    def set(self, k, v):
        try:
            item = self.query.filter(KeyValueItem.key == k).one()
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


class KeyValueMemory(KeyValueStore):
    def __init__(self, separator='.'):
        super(KeyValueMemory, self).__init__(
            path=':memory:', separator=separator)
