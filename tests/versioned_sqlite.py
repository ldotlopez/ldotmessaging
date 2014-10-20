#!/usr/bin/python3

import unittest
from ldotcommons.versioned_sqlite import VersionedSqlite
import pdb

class TestVersionedSqlite(unittest.TestCase):
    def setUp(self):
        self._db = VersionedSqlite(':memory:')

    def tearDown(self):
        self._db.close()
        del(self._db)

    def test_migrations(self):
        self.assertTrue(self._db.get_schema_version('main') == -1)

        migrations = (self.schema0, self.schema1)
        self._db.setup('main', migrations)

        self.assertTrue(self._db.get_schema_version('main') == len(migrations) - 1)

    def schema0(self, curr):
        curr.execute("""
            CREATE TABLE main (
                col1 VARCHAR
            )""")
        return True

    def schema1(self, curr):
        curr.execute("""
            ALTER TABLE main ADD COLUMN col2 INT
            """)
        return True

if __name__ == '__main__':
    unittest.main()
