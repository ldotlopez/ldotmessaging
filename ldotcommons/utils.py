import urllib.parse
from .decorators import accepts
import os.path
import sys
from xdg.BaseDirectory import xdg_data_home, xdg_config_home, xdg_cache_home


@accepts(str, str)
def url_strip_query_param(url, key):
    p = urllib.parse.urlparse(url)
    # urllib.parse.parse_qs may return items in different order that original,
    # so we avoid use it
    # qs = '&'.join([ "{0}={1}".format(k, v[-1]) for (k,v) in urllib.parse.parse_qs(p.query).items() if k != key ])
    qs = '&'.join([x for x in p.query.split('&') if not x.startswith(key+'=')])

    return urllib.parse.ParseResult(p.scheme, p.netloc, p.path, p.params, qs, p.fragment).geturl()

@accepts(str,str, str)
def url_get_query_param(url, key, default = None):
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

