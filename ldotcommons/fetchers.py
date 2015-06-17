import gzip
import io
from os import path
import socket
from urllib import request, error as urllib_error

from . import logging, utils
from .cache import NullCache, DiskCache


class FetchError(Exception):
    pass


class BaseFetcher(object):
    def fetch(self, url, **opts):
        raise NotImplemented('Method not implemented')


class MockFetcher(BaseFetcher):
    def __init__(self, basedir):
        self._basedir = basedir

    def fetch(self, url, **opts):
        url = utils.slugify(url)

        e = None
        f = path.join(self._basedir, url)
        try:
            fh = open(f)
            buff = fh.read()
            fh.close()

            return buff

        except IOError as e_:
            e = e_.args

        e = (e[0], e[1], "'{}'".format(f))
        raise FetchError(*e)


class UrllibFetcher(BaseFetcher):
    def __init__(self, headers={}, cache=False, cache_delta=-1, logger=None):
        if not logger:
            logger = logging.get_logger('ldotcommons.fetchers')

        self._logger = logger.getChild('urllibfetcher')

        if cache:
            cache_path = utils.user_path('cache', 'urllibfetcher',
                                         create=True, is_folder=True)

            self._cache = DiskCache(basedir=cache_path, delta=cache_delta,
                                    logger=self._logger.getChild('diskcache'))

            msg = 'UrllibFetcher using cache {path}'
            msg = msg.format(path=cache_path)
            self._logger.debug(msg)
        else:
            self._cache = NullCache()

        self._headers = headers

    def fetch(self, url, **opts):
        buff = self._cache.get(url)
        if buff:
            self._logger.debug("found in cache: {}".format(url))
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
            raise FetchError("{message}".format(message=e))

        self._logger.debug("stored in cache: {}".format(url))
        self._cache.set(url, buff)
        return buff
