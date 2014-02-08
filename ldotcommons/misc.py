import urllib.parse
from .decorators import accepts

@accepts(str)
def i18n_t(x):
    return x

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

