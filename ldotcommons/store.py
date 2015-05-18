def type_validator(type_table, cast=False, relaxed=False):
    _str_booleans = (
        '0', '1',
        'yes', 'no',
        'true', 'false'
    )

    def _validator(k, v):
        if k not in type_table:
            if relaxed:
                return v
            else:
                raise TypeError(k + ": can't validate")

        req_type = type_table[k]
        if isinstance(v, req_type):
            return v

        if req_type is bool:
            if isinstance(v, str) and v.lower() in _str_booleans:
                return v in (
                    x for (idx, x) in enumerate(_str_booleans) if idx % 2
                )
            else:
                raise TypeError(k + ": can't validate")

        try:
            return req_type(v)
        except ValueError:
            pass

        raise TypeError(k + ": invalid type")

    return _validator


class Store(dict):
    """
    Key-value store using a namespace schema.
    Namespace separator is dot ('.') character
    """
    def __init__(self, d={}, validator=None):
        super(Store, self).__init__()
        self._validator = validator
        for (k, v) in d.items():
            self.__setitem__(k, v)

    def set(self, key, value):
        return self.__setitem__(key, value)

    def get(self, key):
        return self.__getitem__(key)

    def delete(self, key):
        return self.__delitem__(key)

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError()

        store = super(Store, self)
        if self._validator:
            value = self._validator(key, value)

        if '.' not in key:
            store.__setitem__(key, value)

        else:
            key, subkey = key.split('.', 1)

            if key not in self:
                store.__setitem__(key, Store({subkey: value}))

            else:
                store.__getitem__(key).__setitem__(subkey, value)

    def __getitem__(self, key):
        store = super(Store, self)

        if '.' not in key:
            return store.__getitem__(key)

        else:
            key, subkey = key.split('.', 1)
            substore = store.__getitem__(key)

            try:
                return substore.__getitem__(subkey)
            except KeyError as e:
                raise KeyError(key + '.' + e.args[0])

    def __delitem__(self, key):
        store = super(Store, self)

        if '.' not in key:
            store.__delitem__(key)

        else:
            key, subkey = key.split('.', 1)
            store.__getitem__(key).__delitem__(subkey)

    def __contains__(self, key):
        store = super(Store, self)

        if '.' not in key:
            return store.__contains__(key)

        else:
            key, subkey = key.split('.', 1)
            try:
                return store.__getitem__(key).__contains__(subkey)
            except KeyError:
                return False


class AttrStore(Store):
    def __setitem__(self, key, value):
        if '.' not in key:
            setattr(self, key, value)
        else:
            key, subkey = key.split('.', 1)
            setattr(self, key, AttrStore({subkey: value}))

    def __getattr__(self, attr):
        s = super(AttrStore, self)
        if s.__contains__(attr):
            return s.__getitem__(attr)
        else:
            return s.__getattr__(attr)
