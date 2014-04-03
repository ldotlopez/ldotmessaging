from ldotcommons import utils


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage {} messenger_name args…".format(sys.argv[0]))
        sys.exit(1)

    obj = utils.Factory(__package__)(sys.argv[1])
    obj.send(sys.argv[2], '\n'.join(sys.argv[3:]))
