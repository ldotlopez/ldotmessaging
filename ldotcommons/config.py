from argparse import ArgumentParser
from configparser import SafeConfigParser
from os.path import join

from xdg.BaseDirectory import xdg_config_home


class CombinedParser(ArgumentParser):
    # http://blog.vwelch.com/2011/04/combining-configparser-and-argparse.html

    def __init__(self, defaults_cp=None, defaults_path=None, from_cls=None, *args, **kwargs):
        if from_cls:
            defaults_path = config_path_for_class(cls)           

        if defaults_path:
            defaults_cp = SafeConfigParser()
            defaults_cp.read([defaults_path])

        super(CombinedParser, self).__init__(*args, **kwargs)

        items = dict(defaults_cp.items(defaults_cp.default_section))

        for sect in defaults_cp.sections():
            for (k, v) in defaults_cp.items(sect):
                if k not in items:
                    k_ = sect.replace('.','_') + '_' + k
                else:
                    k_ = k
                items[k_] = v

        self.set_defaults(**items)
        self.config_parser = defaults_cp


def config_path_for_class(cls):
    return join(xdg_config_home, cls.__name__.lower() + '.ini')


