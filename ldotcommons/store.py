class Store(dict):
    def __init__(self, d={}):
        super(Store, self).__init__()
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


class ValidatedStore(Store):
    def __init__(self, d={}, validator=None):
        self._validator = validator
        super(ValidatedStore, self).__init__(d)

    def __setitem__(self, key, value):
        if self._validator and not self._validator(key, value):
            raise ValueError(value)

        super(ValidatedStore, self).__setitem__(key, value)


class AttrStore(Store):
    def __getattr__(self, attr):
        rd = super(Store, self)

        if attr not in self:
            rd.__setitem__(attr, AttrStore())

        return rd.__getitem__(attr)

    def __setattr__(self, attr, value):
        rd = super(Store, self)

        return rd.__setitem__(attr, value)
