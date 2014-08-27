if __name__ == '__main__':
    import argparse
    import configparser
    import inspect
    import importlib
    import sys

    parser = argparse.ArgumentParser(description='Messaging microframework.')
    parser.add_argument(
        '-b',
        dest='backend',
        required=True,
        help='Backend')
    parser.add_argument(
        '-c',
        dest='config_file',
        default=None,
        help='Config file')
    parser.add_argument(
        '-i',
        dest='init_section',
        default='init',
        help='Init section')
    parser.add_argument(
        '-s',
        dest='send_section',
        default='send',
        help='Send section')

    init_opts, send_opts = {}, {}

    (opts, other) = parser.parse_known_args(sys.argv[1:])

    # Parse config file
    if opts.config_file:
        cp = configparser.ConfigParser()
        cp.read(opts.config_file)

        try:
            init_opts.update(
                {k: v for (k, v) in cp[opts.init_section].items()}
            )
        except KeyError:
            pass

        try:
            send_opts.update(
                {k: v for (k, v) in cp[opts.send_section].items()}
            )
        except KeyError:
            pass

    # Parse cmdl_opts
    parser = argparse.ArgumentParser()
    for arg in other:
        if not arg.startswith('--'):
            break

        arg = arg.split('=')[0]
        parser.add_argument(
            arg,
            dest=arg[2:].replace('-', '_').replace(' ', '_'))

    parser.add_argument('message', nargs='+')

    cmdl_opts = parser.parse_args(other)

    for (name, value) in vars(cmdl_opts).items():
        if name.startswith('init_'):
            init_opts[name[5:]] = value
        else:
            send_opts[name] = value

    backend_mod = importlib.import_module('ldotcommons.messaging.'+opts.backend)
    backend_cls_name = ''.join([x.capitalize() for x in opts.backend.split('_')])
    backend_cls = getattr(backend_mod, backend_cls_name)

    sig = inspect.signature(backend_cls)
    init_opts = {k: v for (k, v) in init_opts.items() if sig.parameters.get(k)}

    sig = inspect.signature(backend_cls.send)
    send_opts = {k: v for (k, v) in send_opts.items() if sig.parameters.get(k)}

    message = ' '.join(cmdl_opts.message)

    backend_cls(**init_opts).send(message, **send_opts)
