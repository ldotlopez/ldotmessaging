#!/usr/bin/python3

import os
import tempfile
import unittest

from ldotcommons.keyvaluestore import KeyValueStore


class TestMisc(unittest.TestCase):
    def setUp(self):
        fh, path = tempfile.mkstemp()
        self.path = path
        self.store = KeyValueStore(path)

    def tearDown(self):
        os.unlink(self.path)

    def test_basics(self):
        tests = [
            ('bool_true', True),
            ('bool_false', False),
            ('int', 1),
            ('float', 1.2),
            ('char', 'bar'),
            ('jsonable', {'foo': 'bar', 'test': 1})
        ]

        for (k, v) in tests:
            self.store.set(k, v)

        for (k, expected_value) in tests:
            store_value = self.store.get(k)
            self.assertEqual(expected_value, store_value)

    def test_reset(self):
        self.store.set('foo', 1)
        self.store.reset('foo')
        with self.assertRaises(KeyError):
            self.store.get('foo')

    def test_defaults(self):
        self.assertEqual(self.store.get('nothing', default='foo'), 'foo')
        with self.assertRaises(KeyError):
            self.store.get('nothing_2')

    def test_override(self):
        self.store.set('foo', 18)
        self.assertEqual(self.store.get('foo'), 18)

        self.store.set('foo', 81)
        self.assertEqual(self.store.get('foo'), 81)

    def test_children(self):
        self.store.set('a.b', 1)
        self.store.set('a.c', 2)

        self.assertEqual(
            ['a.b', 'a.c'],
            sorted(self.store.children('a')))

        self.assertEqual(list(self.store.children('nothing')), [])

if __name__ == '__main__':
    unittest.main()
