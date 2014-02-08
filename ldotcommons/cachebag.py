import os
import hashlib
import tempfile
import shutil
import time
import logging
import pdb

_ = lambda x : x

class CacheBag(object):
    def __init__(self, basedir = None, delta = -1, logger = logging.getLogger('CacheBag')):
        self._is_tmp  = False
        self._basedir = basedir
        self._delta   = delta
        self._logger  = logger

        if not self._basedir:
            self._basedir = tempfile.mkdtemp()
            self._is_tmp = True

    def _hashfunc(self, key):
        return hashlib.sha1(key).hexdigest()

    def _on_disk_path(self, key):
        hashed = self._hashfunc(key)
        return os.path.join(self._basedir, hashed[:0], hashed[:1], hashed[:2], hashed)

    def set(self, key, value):
        p = self._on_disk_path(key)
        dname = os.path.dirname(p)

        if not os.path.exists(dname):
            os.makedirs(dname)

        try:
            fh = open(p, 'wb')
            fh.write(value)
        except IOError:
            pdb.set_trace()
        except TypeError:
            pdb.set_trace()
        finally:
            fh.close()

    def get(self, key):
        on_disk = self._on_disk_path(key)
        try:
            s = os.stat(on_disk)
        except OSError:
            self._logger.debug(_('Cache fail for {0}'.format(key)))
            return None
        except IOError:
            self._logger.debug(_('Cache fail for {0}'.format(key)))
            return None

        if self._delta >= 0 and (time.mktime(time.localtime()) - s.st_mtime > self._delta):
            self._logger.debug(_('Key {0} is outdated').format(key))
            os.unlink(on_disk)
            return None

        try:
            with open(on_disk) as fh:
                buff = fh.read()
                fh.close()
                return buff
        except IOError:
            self._logger.debug(_('Failed access to key {0}').format(key))
            try:
                os.unlink(on_disk)
            except:
                pass
            return None

    def __del__(self):
        if self._is_tmp:
            shutil.rmtree(self._basedir)

