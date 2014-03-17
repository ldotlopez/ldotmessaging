#!/usr/bin/python3

import unittest
from ldotcommons.decorators import accepts, VaArgs, ArgCountError

class TestDecorators(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @accepts(object, bool, int, float, str)
    def basic_func(self, b, i, f, s):
        pass

    @accepts(object, bool, int, float, str, VaArgs)
    def va_args_func(self, b, i, f, s, *args):
        pass

    @accepts(object, bool, int, float, str, VaArgs)
    def va_args_2_func(self, b, i, f, s, *kwargs):
        pass


    def test_basic(self):
        self.basic_func(True, 1, 1.0, 'str')

    def test_arg_count(self):
        try:
            self.basic_func(True, 1, 1.0)
        except ArgCountError:
            pass

    def test_arg_type(self):
        try:
            self.basic_func('str', 1.0, 1, True)
        except TypeError:
            pass

    def test_va_args(self):
        self.va_args_func(True, 1, 1.0, 'str', 'a', 'b', 'c')
 
if __name__ == '__main__':
    unittest.main()
