import os.path
import re
import socket
import urllib.request

from . import logging
from .cache import NullCache, DiskCache
from .utils import prog_cachedir

_logger = logging.get_logger('ldotcommons.fetchers')


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
    def __init__(self, headers={}, use_cache=False):
        if use_cache:
            cache_path = prog_cachedir('urllibfetcher', create=True)
            self._cache = DiskCache(basedir=cache_path)
            _logger.debug('UrllibFetcher using cache {}'.format(cache_path))
        else:
            self._cache = NullCache()

        self._headers = headers

    def fetch(self, url, **opts):
        buff = self._cache.get(url)
        if buff:
            _logger.debug("found in cache: {}".format(url))
            return buff

        try:
            request = urllib.request.Request(url, headers=self._headers, **opts)
            fh = urllib.request.urlopen(request)
            buff = fh.read()
        except (socket.error, urllib.error.HTTPError) as e:
            raise FetchError("Unable to fetch {0}: {1}".format(url, e))

        _logger.debug("stored in cache: {}".format(url))
        self._cache.set(url, buff)
        return buff
