import unittest
import os

from ldotcommons import utils

import appdirs

# appdirs.system 'darwin'
# appdirs.system 'linux'

# def prog_name
# def prog_basic_configfile
# def prog_configfile
# def prog_datafile
# def prog_cachedir


class UserPathsOSX(unittest.TestCase):
    def setUp(self):
        appdirs.system = 'darwin'

    def test_prog_name(self):
        self.assertEqual(utils.prog_name('simple'), 'Simple')
        self.assertEqual(utils.prog_name('foo-bar'), 'Foo Bar')
        self.assertEqual(utils.prog_name('foo-bar.py'), 'Foo Bar')
        self.assertEqual(utils.prog_name('a.b.py'), 'A.b')

    def test_basic_configfile(self):
        self.assertEqual(
            utils.prog_config_file(),
            os.path.expanduser('~/Library/Application Support/Userpaths.ini'))

    def test_config(self):
        self.assertEqual(
            utils.user_path('config'),
            os.path.expanduser('~/Library/Application Support/Userpaths'))

        self.assertEqual(
            utils.user_path('config', 'foo.cfg'),
            os.path.expanduser('~/Library/Application Support/Userpaths/foo.cfg'))

    def test_user_data(self):
        self.assertEqual(
            utils.user_path('data'),
            os.path.expanduser('~/Library/Application Support/Userpaths'))

        self.assertEqual(
            utils.user_path('data', 'foo'),
            os.path.expanduser('~/Library/Application Support/Userpaths/foo'))

    def test_user_cache(self):
        self.assertEqual(
            utils.user_path('cache'),
            os.path.expanduser('~/Library/Caches/Userpaths'))

        self.assertEqual(
            utils.user_path('cache', 'foo'),
            os.path.expanduser('~/Library/Caches/Userpaths/foo'))


class UserPathsLinux(unittest.TestCase):
    def setUp(self):
        appdirs.system = 'linux'

    def test_prog_name(self):
        self.assertEqual(utils.prog_name('simple'), 'simple')
        self.assertEqual(utils.prog_name('foo-bar'), 'foo-bar')
        self.assertEqual(utils.prog_name('foo-bar.py'), 'foo-bar')
        self.assertEqual(utils.prog_name('a.b.py'), 'a.b')

    def test_basic_configfile(self):
        self.assertEqual(
            utils.prog_config_file(),
            os.path.expanduser('~/.config/userpaths.ini'))

    def test_configfile(self):
        self.assertEqual(
            utils.user_path('config'),
            os.path.expanduser('~/.config/userpaths'))

        self.assertEqual(
            utils.user_path('config', 'foo.cfg'),
            os.path.expanduser('~/.config/userpaths/foo.cfg'))

    def test_user_data_dir(self):
        self.assertEqual(
            utils.user_path('data'),
            os.path.expanduser('~/.local/share/userpaths'))

        self.assertEqual(
            utils.user_path('data', 'foo'),
            os.path.expanduser('~/.local/share/userpaths/foo'))

    def test_user_cache(self):
        self.assertEqual(
            utils.user_path('cache'),
            os.path.expanduser('~/.cache/userpaths'))

        self.assertEqual(
            utils.user_path('cache', 'foo'),
            os.path.expanduser('~/.cache/userpaths/foo'))


if __name__ == '__main__':
    unittest.main()
