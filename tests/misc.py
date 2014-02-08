#!/usr/bin/python3

import unittest
from ldotcommons.misc import url_strip_query_param, url_get_query_param

class TestMisc(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_url_param_get(self):
        u = 'http://test.com/?foo=bar&abc=def&z=1'

        # Get foo
        self.assertEqual(url_get_query_param(u, 'foo'), 'bar')

        # Get non existent parameter
        self.assertRaises(KeyError, url_get_query_param, u, 'xxxx')

    def test_url_param_strip(self):
        u = 'http://test.com/?foo=bar&abc=def&z=1'

        # Non existent parameter
        self.assertEqual(url_strip_query_param(u, 'xxx'), u)

        # Try some variations
        self.assertEqual(url_strip_query_param(u, 'foo'), 'http://test.com/?abc=def&z=1')
        self.assertEqual(url_strip_query_param(u, 'abc'), 'http://test.com/?foo=bar&z=1')
        self.assertEqual(url_strip_query_param(u, 'z'),   'http://test.com/?foo=bar&abc=def')

        # Check corner cases
        u = 'http://test.com/?'
        self.assertEqual(url_strip_query_param(u, 'xxx'), u)

if __name__ == '__main__':
    unittest.main()
