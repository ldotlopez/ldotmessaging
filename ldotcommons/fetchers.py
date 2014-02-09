import urllib.request
import socket

from .cache import NullCache, DiskCache
from .utils import prog_cachedir


class FetchError(Exception):
    pass


class BaseFetcher(object):
    def fetch(self, url, **opts):
        raise NotImplemented('Method not implemented')


class UrllibFetcher(BaseFetcher):
    def __init__(self, use_cache=False):
        if use_cache:
            self._cache = DiskCache(basedir=prog_cachedir('urllibfetcher', create=True))
        else:
            self._cache = NullCache()

    def fetch(self, url, **opts):
        buff = self._cache.get(url)
        if buff:
            return buff

        try:
            buff = urllib.request.urlopen(url).read()
        except (socket.error, urllib.error.HTTPError) as e:
            raise FetchError("Unable to fetch {0}: {1}".format(url, e))

        self._cache.set(url, buff)
        return buff
