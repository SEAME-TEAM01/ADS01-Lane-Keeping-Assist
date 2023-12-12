# ------------------------------------------------------
# Import library
import  sys
import  argparse

# ------------------------------------------------------
# Args Loaders
def load_args():
    args = argparse.ArgumentParser(description='Data-recorder')

    # application default
    args.add_argument( # debug
        '--debug',
        action  = 'store_true',
        dest    = 'debug',
        help    = 'print debug informations'
    )
    args.add_argument( # host
        '--host',
        metavar = 'H',
        default = 'localhost',
        help    = 'IP of the host server (default: 127.0.0.1)')
    args.add_argument( # port
        '--port',
        metavar = 'P',
        default = 2000,
        type    = int,
        help    = 'TCP port to listen to (default: 2000)')
    args.add_argument( # resolutions
        '--res',
        metavar = 'WIDTHxHEIGHT',
        default = '1280x720',
        help    = 'window resolution (default: 1280x720)')
    args.add_argument( # available option list
        '--list',
        action  = 'store_true',
        help    = 'list available options'
    )

    if len(sys.argv) < 1:
        raise RuntimeError(args.format_help())

    args = args.parse_args()
    args.width, args.height = [int(arg) for arg in args.res.split('x')]

    return args