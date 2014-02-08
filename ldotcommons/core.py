import os
from configparser import ConfigParser
from pkgutil import iter_modules

def argument(*args, **kwargs):
    """argparse argument wrapper to ease the command argument definitions"""
    def wrapped_arguments():
        return args, kwargs
    return wrapped_arguments

class PkgMng(object):

    def __init__(self, paths=[]):
        self._paths = paths
        self._addons = None

    def add_addon(self, name, obj):
        self.get_available_addons()

        self._addons[name] = obj

    def get_available_addons(self):
        if self._addons is not None:
            return self._addons
        self._addons = {}

        modules = [(module_loader, name, ispkg) for (module_loader, name, ispkg) in list(iter_modules(self._paths))]
        for (module_loader, name, ispkg) in modules:
            objs = self.inspect_for_addons(module_loader, name, ispkg)
            if isinstance(objs, dict):
                self._addons.update(objs)

        return self._addons

    def get_addon(self, name):
        addons = self.get_available_addons()
        return addons.get(name, None)

    def inspect_for_addons(self, module_loader, name, ispkg):
        raise NotImplementedError()
