import itertools
from glob import fnmatch

_undef = object()
_str_booleans = (
    '0', '1',
    'yes', 'no',
    'y', 'n',
    'true', 'false'
)


class NonEmptyStr(str):
    pass


def cast_value(v, req_type):
    if isinstance(v, req_type):
        return v

    if req_type is int:
        return int(v)

    if req_type is NonEmptyStr:
        v = str(v)
        if v is None or v == '':
            raise ValueError(v)
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
    except ValueError as e:
        raise ValueError(v) from e


def type_validator(type_table, cast=False, relaxed=False):
    def _validator(k, v):
        # Check for exact match
        if k in type_table:
            try:
                return cast_value(v, type_table[k])
            except ValueError():
                pass
            raise TypeError(k + ": invalid type")

        # Check wildcards (regexps in the future?)
        for (candidate_key, candidate_type) in type_table.items():
            if fnmatch.fnmatch(k, candidate_key):
                try:
                    return cast_value(v, candidate_type)
                except ValueError():
                    pass
                raise TypeError(k + ": invalid type")

        # No matches
        if relaxed:
            return v

        # Finally raise a typeerror
        raise TypeError(k + ": can't validate")

    return _validator


class Store(dict):
    """
    Key-value store using a namespace schema.
    Namespace separator is dot ('.') character
    """
    def __init__(self, d={}, validator=None):
        super(Store, self).__init__()

        self._validators = {}
        self._namespaces = set()

        if validator:
            self.set_validator(validator)

        for (k, v) in d.items():
            self.__setitem__(k, v)

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

    @staticmethod
    def get_namespaces(key):
        parts = key.split('.')
        return ('.'.join(parts[0:i+1]) for i in range(len(parts)-1))

    def has_namespace(self, namespace):
        return namespace in self._namespaces

    def set_validator(self, func, ns=None, recheck=True):
        if ns in self._validators:
            raise Exception('Validator conflict')

        self._validators[ns] = func

        if recheck:
            # Dont use .children method here
            subkeys = self.keys()
            if ns:
                s = ns + '.'
                subkeys = filter(lambda k: k.startswith(s), subkeys)

            for k in subkeys:
                self.set(k, self.get(k))

    def find_validator(self, key):
        for ns in reversed([None] + list(self.get_namespaces(key))):
            if ns in self._validators:
                return self._validators[ns]

    def __setitem__(self, key, value):
        if not isinstance(key, str) or key == '':
            raise TypeError(key)

        # Namespaces can't be overwritten
        if key in self._namespaces:
            raise TypeError(key)

        validator = self.find_validator(key)
        if validator:
            value = validator(key, value)

        for x in self.get_namespaces(key):
            self._namespaces.add(x)

        super().__setitem__(key, value)

    def get_tree(self, namespace):
        if namespace not in self._namespaces:
            raise KeyError(namespace)

        r = {}
        idx = len(namespace) + 1
        for subkey in self.children(namespace, fullpath=True):
            if subkey in self._namespaces:
                r[subkey[idx:]] = self.get_tree(subkey)
            else:
                r[subkey[idx:]] = self.get(subkey)

        return r

    def __delitem__(self, key):
        if key in self._namespaces:
            children = list(self.children(key, fullpath=True))
            for child in children:
                del(self[child])
            self._namespaces.remove(key)
        else:
            super().__delitem__(key)

    def children(self, key, fullpath=False):
        s = key + '.'
        r = itertools.chain((k for k in self), self._namespaces)

        # Filter children…
        r = filter(lambda k: k.startswith(s), r)

        # …but not grandchildrens
        r = filter(lambda k: '.' not in k[len(s):], r)

        # Full or short path?
        if not fullpath:
            r = map(lambda k: k[len(s):], r)

        return r

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

    # def _recheck(self, ns=None):
    #     def _sub_stores():
    #         return [ns + '.' + k if ns else k for k in self if isinstance(k, Store)]

    #     def _sub

    #     root = self if not ns else self.get(ns, Store({}))

    #     sub_stores = []
    #     sub_keys = []
    #     for (k, v) in root.items():
    #         (sub_stores if isinstance(v, Store) else sub_keys).append(k)

    #     # Deep recheck
    #     for k in sub_keys:
    #         root.set(k, root.get(k))

    #     for k in sub_stores:
    #         self._recheck
    #     # Wait, must we recheck everything in under ns?
    #     # if not recheck:
    #     #     return

    #     # root = self if ns is None else self.get(ns, Store({}))
    #     # self._rebuild(root)

    # def __setitem__(self, key, value):
    #     if not isinstance(key, str):
    #         raise TypeError()

    #     store = super(Store, self)

    #     # Validate value
    #     parts = key.split('.')
    #     nss = ['.'.join(parts[0:i+1]) for i in range(len(parts)-1)]
    #     for ns in reversed([None] + nss):
    #         if ns in self._validators:
    #             value = self._validators[ns](key, value)
    #             break

    #     if '.' not in key:
    #         store.__setitem__(key, value)

    #     else:
    #         key, subkey = key.split('.', 1)

    #         if key not in self:
    #             store.__setitem__(key, Store({subkey: value}))

    #         else:
    #             store.__getitem__(key).__setitem__(subkey, value)

    # def __getitem__(self, key):
    #     store = super(Store, self)

    #     if '.' not in key:
    #         return store.__getitem__(key)

    #     else:
    #         key, subkey = key.split('.', 1)
    #         substore = store.__getitem__(key)

    #         try:
    #             return substore.__getitem__(subkey)
    #         except KeyError as e:
    #             raise KeyError(key + '.' + e.args[0])

    # def __delitem__(self, key):
    #     store = super(Store, self)

    #     if '.' not in key:
    #         store.__delitem__(key)

    #     else:
    #         key, subkey = key.split('.', 1)
    #         store.__getitem__(key).__delitem__(subkey)

    # def __contains__(self, key):
    #     store = super(Store, self)

    #     if '.' not in key:
    #         return store.__contains__(key)

    #     else:
    #         key, subkey = key.split('.', 1)
    #         try:
    #             return store.__getitem__(key).__contains__(subkey)
    #         except KeyError:
    #             return False


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
