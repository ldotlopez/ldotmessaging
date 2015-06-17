#!/usr/bin/env python

import unittest

import os
import tempfile
import random

from ldotcommons import fetchers, logging, utils


class TestFactory(unittest.TestCase):
    def test_factory(self):
        d = [
            ('mock', fetchers.MockFetcher),
            ('urllib', fetchers.UrllibFetcher)
        ]

        for (name, cls) in d:
            f = fetchers.Fetcher(name)
            self.assertTrue(isinstance(f, cls))


class TestMock(unittest.TestCase):
    def test_fetch(self):
        url = 'http://this-is-a-fake-url.com/sample.html'

        base = tempfile.mkdtemp()
        mockfile = os.path.join(base, utils.slugify(url))

        randstr = str(random.random())
        with open(mockfile, 'w+') as fh:
            fh.write(randstr)
            fh.close()

        fetcher = fetchers.MockFetcher(basedir=base)
        buff = fetcher.fetch(url)

        self.assertEqual(buff, randstr)


class TestUrllib(unittest.TestCase):
    def test_fetch(self):
        url = 'http://google.co.uk/'

        fetcher = fetchers.UrllibFetcher(cache=False)
        buff = fetcher.fetch(url).decode('iso-8859-1')
        self.assertTrue(buff.index('<') >= 0)



if __name__ == '__main__':
    logging.set_level(0)
    unittest.main()
