import configparser
import datetime
import importlib
import os
import re
import sys
import time
import urllib.parse

from xdg.BaseDirectory import xdg_data_home, xdg_config_home, xdg_cache_home


def url_strip_query_param(url, key):
    p = urllib.parse.urlparse(url)
    # urllib.parse.urllib.parse.parse_qs may return items in different order that original,
    # so we avoid use it
    # qs = '&'.join([ "{0}={1}".format(k, v[-1]) for (k,v) in urllib.parse.urllib.parse.parse_qs(p.query).items() if k != key ])
    qs = '&'.join([x for x in p.query.split('&') if not x.startswith(key+'=')])

    return urllib.parse.ParseResult(p.scheme, p.netloc, p.path, p.params, qs, p.fragment).geturl()


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
    return "…" + s[-(length-1):] if len(s) > length else s


def utcnow_timestamp():
    return int(time.mktime(datetime.datetime.utcnow().timetuple()))


def ini_load(path):
    cp = configparser.ConfigParser()
    if cp.read(path) != [path]:
        raise IOError("Can't read {}".format(path))

    return {section: {k: v for (k, v) in cp[section].items()} for section in cp.sections()}


def ini_dump(d, path):
    cp = configparser.ConfigParser()

    for (section, pairs) in d.items():
        cp[section] = {k: v for (k,v) in pairs.items()}

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


def parse_size(string):
    _table = {key: 1000**(idx+1) for (idx, key) in enumerate(['k', 'm', 'g', 't'])}

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
        raise Exception("Unable to import module '{}' for '{}'".format(module, symbol_str))

    try:
        return getattr(m, function)
    except AttributeError:
        pass

    # Try direct import
    try:
        return importlib.import_module(symbol_str)
    except ImportError:
        raise Exception("Unable to locate symbol '{}' for '{}'".format(symbol_str, module))
