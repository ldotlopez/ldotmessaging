import unittest


from ldotcommons import utils


class SingleA(object, metaclass=utils.SingletonMetaclass):
    pass


class SingleB(metaclass=utils.SingletonMetaclass):
    pass


class TestSingleton(unittest.TestCase):
    def test_basic(self):
        a1 = SingleA()
        a2 = SingleA()

        self.assertEqual(a1, a2)
        self.assertTrue(isinstance(a1, SingleA))

    def test_multisingleton(self):
        a1 = SingleA()
        a2 = SingleA()
        b = SingleB()

        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, b)


if __name__ == '__main__':
    unittest.main()
