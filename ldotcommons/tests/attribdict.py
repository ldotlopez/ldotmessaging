import unittest


from ldotcommons import utils


class AttribDictWithRO(utils.AttribDict):
    RO = ['foo']


class AttibDictWithAccessors(utils.AttribDict):
    SETTERS = ['foo']
    GETTERS = ['bar']

    def set_foo(self, value):
        return self._setter('foo', value + 1)

    def get_bar(self):
        return self._getter('bar') - 1


class TestAttribDict(unittest.TestCase):
    def test_init_named_params(self):
        ad = utils.AttribDict(a=1, b=2)
        self.assertTrue('a' in ad)
        self.assertTrue('b' in ad)
        self.assertFalse('c' in ad)
        self.assertEqual(ad.a, 1)
        self.assertEqual(ad.b, 2)

    def test_init_from_dict(self):
        ad = utils.AttribDict({'a': 1, 'b': 2})
        self.assertTrue('a' in ad)
        self.assertTrue('b' in ad)
        self.assertFalse('c' in ad)
        self.assertEqual(ad.a, 1)
        self.assertEqual(ad.b, 2)

    def test_init_from_kwargs(self):
        ad = utils.AttribDict(**{'a': 1, 'b': 2})
        self.assertTrue('a' in ad)
        self.assertTrue('b' in ad)
        self.assertFalse('c' in ad)
        self.assertEqual(ad.a, 1)
        self.assertEqual(ad.b, 2)

    def test_iter(self):
        ad = utils.AttribDict(a=1, b=2)
        self.assertEqual(set(ad.keys()), set(('a', 'b')))

    def test_ro_attribute(self):
        ad = AttribDictWithRO(a=1, b=2, foo=3)
        with self.assertRaises(utils.ReadOnlyAttribute):
            ad.foo = 4

    def test_accessors(self):
        ad = AttibDictWithAccessors()
        ad.foo = 1
        ad.bar = 1
        self.assertEqual(ad.foo, 2)
        self.assertEqual(ad.bar, 0)

if __name__ == '__main__':
    unittest.main()
