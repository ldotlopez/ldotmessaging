from ldotcommons import utils

_factory = utils.Factory('ldotcommons.messaging')
_notifiers = {}


class Notifier:
    def send(self, msg, detail=''):
        raise NotImplementedError()


def enable(notifier, *args, **kwargs):
    if notifier in _notifiers:
        return
    _notifiers[notifier] = _factory(notifier, *args, **kwargs)


def disable(notifier):
    del _notifiers[notifier]


def send(msg, detail=''):
    for n in _notifiers.values():
        n.send(msg, detail)
