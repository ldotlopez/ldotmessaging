from os.path import dirname, basename, join, abspath, isabs
from pkgutil import iter_modules


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PkgMng(object):

    def __init__(self, paths=[]):
        if not all(map(isabs, paths)):
            raise Exception("All paths must be absolute paths")

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


class AppMng(PkgMng):
    def inspect_for_addons(self, module_loader, name, ispkg):
        import ipdb; ipdb.set_trace()
        try:
            m = _import('zizi.apps.' + name + '.app')
        except ImportError as e:
            print("Cannot load %s: %s" % (name, e))
            return None

        appcls = getattr(m, 'App', None)
        if appcls and hasattr(appcls, 'run'):
            return {name: appcls}


def _import(obj):
    mod = __import__(obj)
    for o in obj.split('.')[1:]:
        mod = getattr(mod, o)
    return mod


def get_toplevel_dir():
    """
    Returns the toplevel of zizi
    """
    return dirname(                   # <top>/
        dirname(                      # <top>/zizi/
            dirname(                  # <top>/zizi/core/
                abspath(__file__))))


def get_cache_path(*args):
    """
    Returns the user-cache path for args
    """
    return join(expanduser('~'), '.cache', 'zizi', *args)


def get_persistent_path(*args):
    """
    Returns the user-persistent path for args
    """
    return join(expanduser('~'), '.local', 'share', 'zizi', *args)


def get_user_config_file(app):
    """
    Returns the user-config file for app
    """
    return join(expanduser('~'), '.config', 'zizi', app + '.ini')


def shortify(s, length=50):
    """
    Returns a shortified version of s
    """
    return "…" + s[-(length-1):] if len(s) > length else s


def withconfig(f):
    """
    Decorates methods to read some parameters from config.ini and user-defined
    config
    """
    dname = dirname(sys.modules[f.__module__].__file__)
    appname = basename(dname)

    configfiles = (join(dname, 'config.ini'),
                   get_user_config_file(appname))

    cp = ZiziConfigParser()
    cp.read(configfiles)

    @wraps(f)
    def decorator(*args, **kwargs):
        if 'settings' not in kwargs:
            kwargs['settings'] = cp

        return f(*args, **kwargs)

    return decorator


def utcnow_timestamp():
    return int(time.mktime(datetime.datetime.utcnow().timetuple()))


def word_split(s):
    ret = []
    idx = 0
    protected = False

    for c in s:
        # Setup element
        if len(ret) <= idx:
            ret.insert(idx, '')

        if c in ('\'', '"'):
            protected = not protected
            continue

        if c == ' ' and not protected:
            idx += 1
        else:
            ret[idx] += c

    return ret


def t(s, *args, **kwargs):
    ts = gettext(s)
    if len(args) == 1 and isinstance(args[0], dict):
        return ts.format(**args[0])
    return ts.format(*args, **kwargs)
