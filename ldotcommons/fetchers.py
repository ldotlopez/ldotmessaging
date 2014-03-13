import os.path
import re
import socket
import urllib.request


from .cache import NullCache, DiskCache
from .utils import prog_cachedir


class FetchError(Exception):
    pass


class BaseFetcher(object):
    def fetch(self, url, **opts):
        raise NotImplemented('Method not implemented')


class MockFetcher(BaseFetcher):
    def __init__(self, basedir):
        self._basedir = basedir

    def fetch(self, url, **opts):
        url = re.subn('[^a-z0-9-_\.]', '_', url)[0]

        e = None
        f = os.path.join(self._basedir, url)
        try:
            fh = f.open()
            buff = fh.read()
            fh.close()

            return buff

        except IOError as e_:
            e = e_.args

        e = (e[0], e[1], "'{}'".format(f))
        raise FetchError(*e)


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
            request = urllib.request.Request(url, **opts)
            fh = urllib.request.urlopen(request)
            buff = fh.read()
        except (socket.error, urllib.error.HTTPError) as e:
            raise FetchError("Unable to fetch {0}: {1}".format(url, e))

        self._cache.set(url, buff)
        return buff
