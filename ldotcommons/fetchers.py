import gzip
import io
from os import path
import re
import socket
from urllib import request, error as urllib_error

from . import logging, utils
from .cache import NullCache, DiskCache

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
        f = path.join(self._basedir, url)
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
    def __init__(self, headers={}, cache=False, cache_delta=-1):
        import ipdb; ipdb.set_trace()
        if cache:
            cache_path = utils.user_path('cache', 'urllibfetcher', create=True, is_folder=True)
            self._cache = DiskCache(basedir=cache_path, delta=cache_delta)
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
            req = request.Request(url, headers=self._headers, **opts)
            resp = request.urlopen(req)
            if resp.getheader('Content-Encoding') == 'gzip':
                bi = io.BytesIO(resp.read())
                gf = gzip.GzipFile(fileobj=bi, mode="rb")
                buff = gf.read()
            else:
                buff = resp.read()
        except (socket.error, urllib_error.HTTPError) as e:
            raise FetchError("Unable to fetch {0}: {1}".format(url, e))

        _logger.debug("stored in cache: {}".format(url))
        self._cache.set(url, buff)
        return buff
