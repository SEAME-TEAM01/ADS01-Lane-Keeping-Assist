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

    # actors
    args.add_argument( # actor filter
        '--filter',
        metavar = 'PATTERN',
        default = 'vehicle.*',
        help    = 'actor filter (default: "vehicle.*")'
    )
    args.add_argument( # actor generation
        '--generation',
        metavar = 'G',
        default = '2',
        help    = 'restrict to certain actor generation (values: "1","2","All" - default: "2")'
    )
    args.add_argument( # actor rolename
        '--rolename',
        metavar = 'NAME',
        default = 'hero',
        help    = 'actor role name (default: "hero")'
    )

    # configs
    args.add_argument( # autopilot
        '--autopilot',
        action  = 'store_true',
        help    = 'enable autopilot'
    )
    args.add_argument( # gamma
        '--gamma',
        default = 2.2,
        type    = float,
        help    = 'Gamma correction of the camera (default: 2.2)'
    )
    args.add_argument( # fps
        '--fps',
        metavar = 'N',
        type    = float,
        help    = 'set fixed FPS, zero for variable FPS (similar to --delta-seconds)'
    )
    args.add_argument( # synchronous mode
        '--sync',
        action  = 'store_true',
        help    = 'Activate synchronous mode execution'
    )
    args.add_argument( # inspect simulation        
        '--inspect',
        action  = 'store_true',
        help    = 'inspect simulation'
    )
    
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