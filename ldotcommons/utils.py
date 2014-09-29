import argparse
import configparser
import datetime
import importlib
import os
import re
import sys
import time
import urllib.parse

from xdg.BaseDirectory import xdg_data_home, xdg_config_home, xdg_cache_home


class DictAction(argparse.Action):

    """
    Convert a series of --foo key=value --foo key2=value2 into a dict like:
    { key: value, key2: value}
    """

    def __call__(self, parser, namespace, values, option_string=None):
        dest = getattr(namespace, self.dest)
        if dest is None:
            dest = {}

        parts = values.split('=')
        key = parts[0]
        value = ''.join(parts[1:])

        dest[key] = value

        setattr(namespace, self.dest, dest)


class MultiDepthDict(dict):

    def subdict(self, prefix, strip_prefix=True, separator='.', merge_parent=False):
        full_prefix = prefix + separator

        return {k[len(full_prefix):] if strip_prefix else k: v
                for (k, v) in self.items() if k.startswith(full_prefix)}


class SingletonMetaclass(type):
    def __call__(cls, *args, **kwargs):
        instance = getattr(cls, '_instance', None)
        if not instance:
            setattr(cls, '_instance', super(SingletonMetaclass, cls).__call__(*args, **kwargs))
        return cls._instance


class ReadOnlyAttribute(Exception):
    pass


# class AttribDict(dict):
#     RO = []
#     GETTERS = []
#     SETTERS = []

#     def _setter(self, attr, value):
#         try:
#             return self.__setitem__(attr, value)
#         except KeyError:
#             raise AttributeError(attr)

#     def _getter(self, attr):
#         try:
#             return self.__getitem__(attr)
#         except KeyError:
#             raise AttributeError(attr)

#     def __getattr__(self, attr):
#         if attr in self.__class__.GETTERS:
#             return getattr(self, 'get_' + attr)()

#         try:
#             return super(AttribDict, self).__getitem__(attr)
#         except KeyError:
#             raise AttributeError(attr)

#     def __setattr__(self, attr, value):
#         if attr in self.__class__.RO:
#             raise ReadOnlyAttribute()

#         if attr in self.__class__.SETTERS:
#             import ipdb; ipdb.set_trace()
#             return getattr(self, 'set_' + attr)(value)()

#         try:
#             return super(AttribDict, self).__setitem__(attr, value)
#         except KeyError:
#             raise AttributeError(attr)

#     def __setitem__(self, key, value):
#         try:
#             return self.__setattr__(key, value)
#         except AttributeError:
#             pass

#         raise KeyError(key)

#     def __getitem__(self, key):
#         try:
#             return self.__getattr__(key)
#         except AttributeError:
#             pass

#         raise KeyError(key)

class AttribDict(dict):
    RO = []
    GETTERS = []
    SETTERS = []

    def _setter(self, attr, value):
        try:
            return self.__setitem__(attr, value)
        except KeyError:
            raise AttributeError(attr)

    def _getter(self, attr):
        try:
            return self.__getitem__(attr)
        except KeyError:
            raise AttributeError(attr)

    def __getattr__(self, attr):
        if attr in self.__class__.GETTERS:
            return getattr(self, 'get_' + attr)()

        try:
            return super(AttribDict, self).__getitem__(attr)
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if attr in self.__class__.RO:
            raise ReadOnlyAttribute()

        if attr in self.__class__.SETTERS:
            return getattr(self, 'set_' + attr)(value)

        try:
            return super(AttribDict, self).__setitem__(attr, value)
        except KeyError:
            raise AttributeError(attr)


class FactoryError(Exception):
    pass


class Factory:

    def _to_clsname(self, name):
        return ''.join([
            x.capitalize() for x in self._to_modname(name).split('_')
        ])

    def _to_modname(self, name):
        return name.replace('-', '_')

    def __init__(self, ns):
        self._ns = ns
        self._mod = importlib.import_module(ns)
        self._objs = {}

    def __call__(self, name, *args, **kwargs):
        if name not in self._objs:
            cls = None

            # Try loading class from internal mod
            try:
                cls = self._load_from_ns(name)
            except AttributeError:
                pass

            # Try loading from submodule
            if not cls:
                try:
                    cls = self._load_from_submod(name)
                except (ImportError, AttributeError):
                    pass

            # Module not found
            if not cls:
                raise FactoryError(
                    'Unable to load {} from namespace {}'.format(
                        name, self._ns)
                    )

            # Create and save obj into cache
            self._objs[name] = cls(*args, **kwargs)

        return self._objs[name]

    def _load_from_ns(self, name):
        return getattr(self._mod, self._to_clsname(name))

    def _load_from_submod(self, name):
        m = importlib.import_module(
            "{}.{}".format(self._ns, self._to_modname(name)))
        return getattr(m, self._to_clsname(name))


class ModuleFactory:
    def __init__(self, ns):
        self._ns = ns
        self._ns_sym = importlib.import_module(ns)
        self._m = {}

    def __call__(self, name):
        if name not in self._m:
            if name in self._ns_sym:
                self._m[name] = getattr(self._ns_sym, name)

            else:
                try:
                    self._m[name] = importlib.import_module(
                        "{}.{}".format(self._ns, name))
                except ImportError:
                    pass

        return self._m[name]


class ObjectFactory:
    def __init__(self, ns, in_sub_module=True):
        self._ns = ns
        self._ns_sym = importlib.import_module(ns)
        self._m = {}
        self._in_sub_module = in_sub_module

    def __call__(self, name, *args, **kwargs):
        if name not in self._m:
            cls_name = ''.join([x.capitalize() for x in name.split('_')])

            if not self._in_sub_module:
                self._m[name] = getattr(self._ns_sym, cls_name)

            else:
                tmp = re.sub(r'([A-Z])', r'_\1', cls_name[1:])
                tmp = cls_name[0] + tmp

                sub_mod = None
                sub_mod_exceptions = {}

                for mod_candidate in [cls_name.lower(), tmp.lower()]:
                    try:
                        sub_mod = importlib.import_module("{}.{}".format(
                            self._ns, mod_candidate))
                        break

                    except ImportError as e:
                        sub_mod_exceptions[mod_candidate] = e
                        pass

                if not sub_mod:
                    raise IndexError(sub_mod_exceptions)

            self._m[name] = getattr(sub_mod, cls_name)

        return self._m[name](*args, **kwargs)


def url_strip_query_param(url, key):
    p = urllib.parse.urlparse(url)
    # urllib.parse.urllib.parse.parse_qs may return items in different order
    # that original, so we avoid use it
    qs = '&'.join(
        [x for x in p.query.split('&') if not x.startswith(key + '=')])

    return urllib.parse.ParseResult(
        p.scheme,
        p.netloc,
        p.path,
        p.params,
        qs,
        p.fragment).geturl()


def url_get_query_param(url, key, default=None):
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    if key in q:
        return q[key][-1]
    else:
        return default


def prog_name(prog=os.path.basename(sys.argv[0])):
    return os.path.splitext(prog)[0]


def prog_basic_configfile(prog=os.path.basename(sys.argv[0])):
    return xdg_config_home + '/' + prog_name(prog) + '.ini'


def prog_configfile(name, prog=os.path.basename(sys.argv[0])):
    return xdg_config_home + '/' + prog_name(prog) + '/' + name


def prog_datafile(name, prog=os.path.basename(sys.argv[0]), create=False):
    datafile = xdg_data_home + '/' + prog_name(prog) + '/' + name
    dname, bname = os.path.split(datafile)
    if create and not os.path.exists(dname):
        os.makedirs(dname)

    return datafile


def prog_cachedir(name, prog=os.path.basename(sys.argv[0]), create=False):
    cachedir = xdg_cache_home + '/' + prog_name(prog) + '/' + name
    if create and not os.path.exists(cachedir):
        os.makedirs(cachedir)

    return cachedir


def shortify(s, length=50):
    """
    Returns a shortified version of s
    """
    return "…" + s[-(length - 1):] if len(s) > length else s


def utcnow_timestamp():
    return int(time.mktime(datetime.datetime.utcnow().timetuple()))


def ini_load(path):
    cp = configparser.ConfigParser()

    fh = open(path, 'r')
    cp.read_file(fh)
    fh.close()

    return {section: {k: v for (k, v) in cp[section].items()} for section in cp.sections()}


def ini_dump(d, path):
    cp = configparser.ConfigParser()

    for (section, pairs) in d.items():
        cp[section] = {k: v for (k, v) in pairs.items()}

    fh = open(path, 'w+')
    cp.write(fh)
    fh.close()


def get_debugger():
    debugger = None

    for m in ['ipdb', 'pdb']:
        try:
            mod = importlib.import_module(m)
            return mod
        except ImportError:
            pass

    if debugger is None:
        raise Exception('No debugger available')


def breakpoint():
    get_debugger().set_trace()


def parse_size(string):
    _table = {key: 1000 ** (idx + 1)
              for (idx, key) in enumerate(['k', 'm', 'g', 't'])}

    string = string.replace(',', '.')
    m = re.search(r'^([0-9\.]+)([kmgt]b?)?$', string.lower())
    if not m:
        raise ValueError()

    value = m.group(1)
    mod = m.group(2)

    if '.' in value:
        value = float(value)
    else:
        value = int(value)

    if mod in _table:
        value = value * _table[mod]

    return value


def get_symbol(symbol_str):
    parts = symbol_str.split('.')

    module = '.'.join(parts[:-1])
    function = parts[-1]

    m = None
    try:
        m = importlib.import_module(module)
    except ImportError:
        pass

    if not m:
        raise Exception(
            "Unable to import module '{}' for '{}'".format(module, symbol_str))

    try:
        return getattr(m, function)
    except AttributeError:
        pass

    # Try direct import
    try:
        return importlib.import_module(symbol_str)
    except ImportError:
        raise Exception(
            "Unable to locate symbol '{}' for '{}'".format(symbol_str, module))
