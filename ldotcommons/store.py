from glob import fnmatch

_undef = object()
_str_booleans = (
    '0', '1',
    'yes', 'no',
    'y', 'n',
    'true', 'false'
)


def _cast_value(v, req_type):
    if isinstance(v, req_type):
        return v

    if req_type is bool:
        if isinstance(v, str) and v.lower() in _str_booleans:
            return v in (
                x for (idx, x) in enumerate(_str_booleans) if idx % 2
            )
        else:
            raise ValueError(v)

    try:
        return req_type(v)
    except ValueError:
        pass

    raise ValueError(v)


def type_validator(type_table, cast=False, relaxed=False):

    def _validator(k, v):
        # Check for exact match
        if k in type_table:
            try:
                return _cast_value(v, type_table[k])
            except ValueError():
                pass
            raise TypeError(k + ": invalid type")

        # Check wildcards (regexps in the future?)
        for (candidate_key, candidate_type) in type_table.items():
            if fnmatch.fnmatch(k, candidate_key):
                try:
                    return _cast_value(v, candidate_type)
                except ValueError():
                    pass
                raise TypeError(k + ": invalid type")

        # No matches
        if relaxed:
            return v

        # Finally raise a typeerror
        raise TypeError(k + ": can't validate")

        # Original code
        # if k not in type_table:
        #     if relaxed:
        #         return v
        #     else:
        #         raise TypeError(k + ": can't validate")

        # req_type = type_table[k]
        # if isinstance(v, req_type):
        #     return v

        # if req_type is bool:
        #     if isinstance(v, str) and v.lower() in _str_booleans:
        #         return v in (
        #             x for (idx, x) in enumerate(_str_booleans) if idx % 2
        #         )
        #     else:
        #         raise TypeError(k + ": can't validate")

        # try:
        #     return req_type(v)
        # except ValueError:
        #     pass

        # raise TypeError(k + ": invalid type")

    return _validator


class Store(dict):
    """
    Key-value store using a namespace schema.
    Namespace separator is dot ('.') character
    """
    def __init__(self, d={}, validator=None):
        super(Store, self).__init__()

        self._validators = {}
        if validator:
            self.set_validator(validator)

        for (k, v) in d.items():
            self.__setitem__(k, v)

    def set_validator(self, func, ns=None):
        if ns in self._validators:
            raise Exception('Validator conflict')

        self._validators[ns] = func

    def load_configparser(self, cp, root_sections=()):
        def is_root(x):
            return x in root_sections

        kvs = {}

        for s in filter(is_root, cp.sections()):
            kvs.update({k: v for (k, v) in cp[s].items()})

        for s in filter(lambda x: not is_root(x), cp.sections()):
            kvs.update({s + '.' + k: v for (k, v) in cp[s].items()})

        for (k, v) in kvs.items():
            self.set(k, v)

    def load_arguments(self, args):
        for (k, v) in vars(args).items():
            self.set(k, v)

    def set(self, key, value):
        return self.__setitem__(key, value)

    def get(self, key, default=_undef):
        if key in self:
            return self.__getitem__(key)

        elif default is not _undef:
            return default

        else:
            raise KeyError(key)

    def delete(self, key):
        return self.__delitem__(key)

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError()

        store = super(Store, self)

        # Validate value
        parts = key.split('.')
        nss = ['.'.join(parts[0:i+1]) for i in range(len(parts)-1)]
        for ns in reversed([None] + nss):
            if ns in self._validators:
                value = self._validators[ns](key, value)
                break

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
