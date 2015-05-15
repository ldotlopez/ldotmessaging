import unittest
from ldotcommons import store
import configparser


class TestStore(unittest.TestCase):
    def test_init(self):
        rd = store.Store({
            'x': 1,
            'y': 2,
            'foo.bar': 3.14
        })
        self.assertEqual(rd['x'], 1)
        self.assertEqual(rd['foo.bar'], 3.14)
        with self.assertRaises(KeyError):
            rd['a.b.c']

        rd = store.Store()
        rd['x'] = 1
        self.assertEqual(rd['x'], 1)
        with self.assertRaises(KeyError):
            rd['a.b.c']

    def test_setget(self):
        rd = store.Store()
        rd['x'] = 1

        self.assertEqual(rd['x'], 1)
        with self.assertRaises(KeyError):
            rd['y']

        with self.assertRaises(TypeError):
            rd[1.3] = 1

    def test_update(self):
        rd = store.Store({
            'x': 1,
            'y': 2,
            'foo.bar': 3,
            'foo.raz': 4
        })

        rd['x'] = 'x'
        rd['foo.raz'] = 'y'

        self.assertEqual(rd, {
            'x': 'x',
            'y': 2,
            'foo': {
                'bar': 3,
                'raz': 'y'
            }
        })

    def test_delete(self):
        rd = store.Store({
            'x': 1,
            'y': 2,
            'foo.bar': 3,
            'foo.raz': 4,
            'z.y.a': 5,
            'z.y.b': 6,
            'z.y.c': 7,
        })
        del rd['z.y.c']
        del rd['foo']
        self.assertEqual(rd, {
            'x': 1,
            'y': 2,
            'z': {
                'y': {
                    'a': 5,
                    'b': 6,
                }
            }
        })

    def test_contains(self):
        rd = store.Store({
            'x': 1,
            'y': 2,
            'foo.bar': 3,
            'foo.raz': 4,
            'z.y.a': 5,
            'z.y.b': 6,
            'z.y.c': 7,
        })
        self.assertTrue('x' in rd)
        self.assertTrue('z.y.a' in rd)
        self.assertFalse('bar' in rd)

    def test_keyerror(self):
        rd = store.Store({
            'x.y.z': None
        })
        with self.assertRaises(KeyError) as e:
            rd['x.y.foo']
        self.assertEqual(e.exception.args[0], 'x.y.foo')

        with self.assertRaises(KeyError) as e:
            rd['a.b.c']
        self.assertEqual(e.exception.args[0], 'a')

    def test_builtin_validator(self):
        type_table = {
            'a': int,
            'b': float,
            'c': str,
            'x.y': int
        }

        d = {
            'a': 1,
            'b': 1.2,
            'c': 'foo',
            'x.y': 1
        }

        rd = store.Store(
            d=d,
            validator=store.type_validator(type_table, cast=False))

        rd['a'] = 2
        self.assertEqual(rd['a'], 2)

        with self.assertRaises(TypeError):
            rd['a'] = 'i want a int'

        with self.assertRaises(TypeError):
            rd['z'] = 'this key should not exist'

        with self.assertRaises(TypeError):
            rd['x'] = 'this is a namespace, not a key'

    def test_cast_validator(self):
        data = {
            'intkey': 1,
            'strkey': 'foo',
            'boolkey': True,
            'namespace.test': {'foo': 'bar'}
        }
        types = {
            'intkey': int,
            'strkey': str,
            'boolkey': bool,
            'namespace.test': dict,
            'namespace.test.foo': str
        }
        rd = store.Store(
            data,
            validator=store.type_validator(types, cast=True))

        rd['intkey'] = '8'
        rd['strkey'] = 0
        rd['boolkey'] = '0'
        rd['namespace.test.foo'] = 1
        self.assertEqual(rd['intkey'], 8)
        self.assertEqual(rd['strkey'], '0')
        self.assertEqual(rd['boolkey'], False)
        self.assertEqual(rd['namespace.test.foo'], '1')

    def test_relaxed_validator(self):
        data = {
            'defined': 1
        }
        types = {
            'defined': int
        }

        rd = store.Store(
            data,
            validator=store.type_validator(types, relaxed=True))
        with self.assertRaises(TypeError):
            rd['defined'] = 'foo'
        rd['undefined'] = object()

        rd = store.Store(
            data,
            validator=store.type_validator(types, relaxed=False))
        with self.assertRaises(TypeError):
            rd['undefined'] = object()
        rd['defined'] = 1


class TestAttrStore(unittest.TestCase):
    def test_simple(self):
        data = {
            'foo': 1,
            'bar.odd': 'x'
        }
        x = store.AttrStore(data)

        self.assertEqual(x.foo, 1)
        self.assertEqual(x.bar.odd, 'x')

        x.bar.odd = 'a'
        self.assertEqual(x.bar.odd, 'a')


class TestConfigLoader(unittest.TestCase):
    ini = """
[main]
a = 1
b = 2

[subsect_a]
c = 3
d = 4

[subsect_b]
e = 5
f = 6

[extensions.importer.foo]
g = 6
h = 7

[extensions.importer.bar]
i = 8
j = 9

[extensions.downloader.zar]
k = 10
"""
    d = {
        'a': '1',
        'b': '2',
        'subsect_a.c': '3',
        'subsect_a.d': '4',
        'subsect_b.e': '5',
        'subsect_b.f': '6',
        'extensions.importer.foo.g': '6',
        'extensions.importer.foo.h': '7',
        'extensions.importer.bar.i': '8',
        'extensions.importer.bar.j': '9',
        'extensions.downloader.zar.k': '10'
    }

    def test_config(self):
        root_sections = ('main', )

        def is_root(x):
            return x in root_sections

        cp = configparser.ConfigParser()
        cp.read_string(self.ini)

        kvs = {}

        for s in filter(is_root, cp.sections()):
            kvs.update({k: v for (k, v) in cp[s].items()})

        for s in filter(lambda x: not is_root(x), cp.sections()):
            kvs.update({s + '.' + k: v for (k, v) in cp[s].items()})

        self.assertEqual(self.d, kvs)

        # cs = store.AttrStore()
        # for (k, v) in kvs.items():
        #     cs[k] = v

        # import ipdb; ipdb.set_trace()
        # self.assertEqual(cs.extensions.importer.foo.g, '6')


if __name__ == '__main__':
    unittest.main()
