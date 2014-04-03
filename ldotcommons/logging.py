#coding: utf-8

#Copyright (C) 2012 Jacobo Tarragón
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from functools import wraps
import logging

from ldotcommons.utils import prog_name


LOGGING_FORMAT = "[%(levelname)s] [%(name)s] %(message)s"

_loggers = dict()


class EncodedStreamHandler(logging.StreamHandler):
    def __init__(self, encoding='utf-8', *args, **kwargs):
        super(EncodedStreamHandler, self).__init__(*args, **kwargs)
        self.encoding = encoding
        self.terminator = self.terminator.encode(self.encoding)

    def emit(self, record):
        try:
            msg = self.format(record).encode(self.encoding)
            stream = self.stream
            stream.buffer.write(msg)
            stream.buffer.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


def get_logger(key=None):
    global _loggers

    if key is None:
        key = prog_name()

    if not key in _loggers:
        _loggers[key] = logging.getLogger(key)
        _loggers[key].setLevel(logging.DEBUG)

        handler = EncodedStreamHandler()
        handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        _loggers[key].addHandler(handler)
    return _loggers[key]


def log_on_success(msg='done', level=20):
    """
    logs `msg` with `level` at the end of the method call
    """
    def decorator(fn):
        @wraps(fn)
        def wrapped_fn(self, *args, **kwargs):
            logger = getattr(self, 'logger')
            ret = fn(self, *args, **kwargs)
            if logger:
                logger.log(level, msg)
            return ret
        return wrapped_fn
    return decorator
