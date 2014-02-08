import os
import collections
import sqlite3
import ldotcommons.exceptions

class MigrationError(Exception): pass

class VersionedSqlite(sqlite3.Connection):
    TBL_NAME = "_schema_versions"

    def __init__(self, dbpath):
        if not os.path.isdir(os.path.dirname(dbpath)):
            os.makedirs(os.path.dirname(dbpath))
        super(VersionedSqlite, self).__init__(dbpath)

    def get_schema_version(self, schema):
        curr = self.cursor()

        res = curr.execute('SELECT name FROM sqlite_master WHERE type = ? AND name = ?', ('table', VersionedSqlite.TBL_NAME))
        if not res.fetchone():
            curr.execute('CREATE TABLE _schema_versions (schema VARCHAR PRIMARY KEY UNIQUE, version)')

        row = curr.execute('SELECT version FROM _schema_versions WHERE schema = ?', (schema,)).fetchone()
        if not row:
            return -1;

        return int(row[0])

    def setup(self, schema, migrations):
        if not all([isinstance(x, collections.Callable) for x in migrations]):
            raise ldotcommons.exceptions.ParamError('migrations must be an iterable of callables')

        curr_vers = self.get_schema_version(schema)
        for ver in range(curr_vers + 1, len(migrations)):
            migration = migrations[ver]
            if migration(self.cursor()):
                self.execute('INSERT OR REPLACE INTO _schema_versions VALUES(?, ?)', (schema, ver))
                self.commit()
            else:
                self.rollback()
                raise MigrationError('Migration {0} failed'.format(ver))

def tuple2dict(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
