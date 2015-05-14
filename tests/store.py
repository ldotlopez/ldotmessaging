import unittest
from ldotcommons import store


class TestRecursiveDict(unittest.TestCase):
    def test_init(self):
        rd = store.RecursiveDict({
            'x': 1,
            'y': 2,
            'foo.bar': 3.14
        })
        self.assertEqual(rd['x'], 1)
        self.assertEqual(rd['foo.bar'], 3.14)
        with self.assertRaises(KeyError):
            rd['a.b.c']

        rd = store.RecursiveDict()
        rd['x'] = 1
        self.assertEqual(rd['x'], 1)
        with self.assertRaises(KeyError):
            rd['a.b.c']

    def test_setget(self):
        rd = store.RecursiveDict()
        rd['x'] = 1

        self.assertEqual(rd['x'], 1)
        with self.assertRaises(KeyError):
            rd['y']

        with self.assertRaises(TypeError):
            rd[1.3] = 1

    def test_update(self):
        rd = store.RecursiveDict({
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
        rd = store.RecursiveDict({
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
        rd = store.RecursiveDict({
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
        rd = store.RecursiveDict({
            'x.y.z': None
        })
        with self.assertRaises(KeyError) as e:
            rd['x.y.foo']
        self.assertEqual(e.exception.args[0], 'x.y.foo')

        with self.assertRaises(KeyError) as e:
            rd['a.b.c']
        self.assertEqual(e.exception.args[0], 'a')


class TestStore(unittest.TestCase):
    def test_simple(self):
        x = store.Store()
        x.foo = 1
        x.bar.odd = 'x'

        self.assertEqual(x.foo, 1)
        self.assertEqual(x.bar.odd, 'x')


class ValidatedRecursiveDict(unittest.TestCase):
    def test_basic_schema(self):
        def validator(k, v):
            # print("{}: {}".format(k, v))
            if k.endswith('_int') and not isinstance(v, int):
                return False

            return True

        foo = store.ValidatedRecursiveDict(validator=validator)
        foo['a_int'] = 1
        foo['b_int'] = 1
        foo['point.x'] = 1.0
        foo['complex.real'] = 1
        foo['complex.imaginary'] = 2
        with self.assertRaises(ValueError):
            foo['key_int'] = 'a'

if __name__ == '__main__':
    unittest.main()
