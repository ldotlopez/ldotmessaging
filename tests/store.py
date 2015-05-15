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


class TestAttrStore(unittest.TestCase):
    def test_simple(self):
        x = store.AttrStore()
        x.foo = 1
        x.bar.odd = 'x'

        self.assertEqual(x.foo, 1)
        self.assertEqual(x.bar.odd, 'x')


class TestValidatedStore(unittest.TestCase):
    def test_basic_schema(self):
        def validator(k, v):
            # print("{}: {}".format(k, v))
            if k.endswith('_int') and not isinstance(v, int):
                return False

            return True

        foo = store.ValidatedStore(validator=validator)
        foo['a_int'] = 1
        foo['b_int'] = 1
        foo['point.x'] = 1.0
        foo['complex.real'] = 1
        foo['complex.imaginary'] = 2
        with self.assertRaises(ValueError):
            foo['key_int'] = 'a'


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
