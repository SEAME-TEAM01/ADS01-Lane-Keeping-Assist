#!/usr/bin/env python

# ------------------------------------------------------
# Goal for this main.py
# - Re-implementation for config.py

"""

"""

# ------------------------------------------------------
# Import base library
import  os
import  re
import  sys
import  glob
import  socket
import  argparse
import  datetime
import  textwrap

# ------------------------------------------------------
# Find Carla module
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except  IndexError:
    pass
import  carla

# ------------------------------------------------------
# Import Custom Files
from    util.colors \
        import  *
from    util.prints \
        import  *
from    util.variables \
        import  *
from    util.utils \
        import  *

# ------------------------------------------------------
# Utils
def find_weather_presets():
    presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]
    return [(getattr(carla.WeatherParameters, x), x) for x in presets]

# ------------------------------------------------------
# Printing
def inspect(_args, _client):
    address = '%s:%d' % (get_ip(_args.host), _args.port)

    world = _client.get_world()
    elapsed_time = world.get_snapshot().timestamp.elapsed_seconds
    elapsed_time = datetime.timedelta(seconds=int(elapsed_time))

    actors = world.get_actors()
    s = world.get_settings()

    weather = 'Custom'
    current_weather = world.get_weather()
    for preset, name in find_weather_presets():
        if current_weather == preset:
            weather = name

    if s.fixed_delta_seconds is None:
        frame_rate = 'variable'
    else:
        frame_rate = '%.2f ms (%d FPS)' % (
            1000.0 * s.fixed_delta_seconds,
            1.0 / s.fixed_delta_seconds)

    print_info("Simulation Inspections:")
    print_term_size_line()
    print_info('address:% 26s' % address, is_first_line=False)
    print_info('version:% 26s\n' % _client.get_server_version(), is_first_line=False)
    print_info('map:        % 22s' % world.get_map().name, is_first_line=False)
    print_info('weather:    % 22s\n' % weather, is_first_line=False)
    print_info('time:       % 22s\n' % elapsed_time, is_first_line=False)
    print_info('frame rate: % 22s' % frame_rate, is_first_line=False)
    print_info('rendering:  % 22s' % ('disabled' if s.no_rendering_mode else 'enabled'), is_first_line=False)
    print_info('sync mode:  % 22s\n' % ('disabled' if not s.synchronous_mode else 'enabled'), is_first_line=False)
    print_info('actors:     % 22d' % len(actors), is_first_line=False)
    print_info('  * spectator:% 20d' % len(actors.filter('spectator')), is_first_line=False)
    print_info('  * static:   % 20d' % len(actors.filter('static.*')), is_first_line=False)
    print_info('  * traffic:  % 20d' % len(actors.filter('traffic.*')), is_first_line=False)
    print_info('  * vehicles: % 20d' % len(actors.filter('vehicle.*')), is_first_line=False)
    print_info('  * walkers:  % 20d' % len(actors.filter('walker.*')), is_first_line=False)
    print_term_size_line()
    print_end()

def list_blueprints(_world, _blueprint_filter):
    blueprint_library = _world.get_blueprint_library()
    blueprints = [bp.id for bp in blueprint_library.filter(_blueprint_filter)]
    print_info(f"available blueprints (filter {_blueprint_filter}):")
    for blueprint in sorted(blueprints):
        print_info(f"{blueprint}", is_first_line=False)
    print_end()

def list_options(_client):
    maps = [m.replace('/Game/Carla/Maps', '') for m in _client.get_available_maps()]
    indent = 4 * ' '
    def wrap(text):
        return '\n'.join(textwrap.wrap(text, initial_indent=indent, subsequent_indent=indent))

    print_info('Weather Presets:')
    print_info(wrap(', '.join(x for _, x in find_weather_presets())) + '.\n', is_first_line=False)
    print_end()

    print_info('Available Maps:')
    print_info(wrap(', '.join(sorted(maps))) + '.\n', is_first_line=False)
    print_end()
# ------------------------------------------------------
# Option Loaders
def load_args():
    args = argparse.ArgumentParser(description=__doc__)

    args.add_argument( # host
        "--host",
        metavar = 'H',
        default = 'localhost',
        help    = 'IP of the host server (default: 127.0.0.1)')
    args.add_argument( # port
        '-p', '--port',
        metavar = 'P',
        default = 2000,
        type    = int,
        help    = 'TCP port to listen to (default: 2000)')
    args.add_argument( # load default options
        '-d', '--default',
        action  = 'store_true',
        help    = 'load_defaultsettings')
    args.add_argument( # map
        '-m', '--map',
        help    = 'load a new map, use --list tp see avaliable maps'    )
    args.add_argument( # map reloading
        '-r', '--reload-map',
        action  = 'store_true',
        help    = 'reload current map')
    args.add_argument( # delta seconds
        '--delta-seconds',
        metavar = 'S',
        type    = float,
        help    = 'set fixed delta seconds, zero for variable frame rate')
    args.add_argument( # fps
        '--fps',
        metavar = 'N',
        type    = float,
        help    = 'set fixed FPS, zero for variable FPS (similar to --delta-seconds)')
    args.add_argument( # enable rendering
        '--rendering',
        action  = 'store_true',
        help    = 'enable rendering')
    args.add_argument( # disable rendering
        '--no-rendering',
        action  = 'store_true',
        help    = 'disable rendering')
    args.add_argument( # synchronous mode
        '--no-sync',
        action  = 'store_true',
        help    = 'disable synchronous mode')
    args.add_argument( # weather
        '--weather',
        help    = 'set weather preset, use --list to see available presets')
    args.add_argument( # inspect simulation        
        '-i', '--inspect',
        action  = 'store_true',
        help    = 'inspect simulation'
    )
    args.add_argument( # available option list
        '-l', '--list',
        action  = 'store_true',
        help    = 'list available options')
    args.add_argument( # list blueprints
        '-b', '--list-blueprints',
        metavar = 'FILTER',
        help    = 'list available blueprints matching FILTER (use \'*\' to list them all)')
    args.add_argument( # minimum physical map
        '-x', '--xodr-path',
        metavar = 'XODR_FILE_PATH',
        help    = 'load a new map with a minimum physical road representation of the provided OpenDRIVE')
    args.add_argument( # osm path
        '--osm-path',
        metavar='OSM_FILE_PATH',
        help='load a new map with a minimum physical road representation of the provided OpenStreetMaps')
    args.add_argument( # tile streaming distance
        '--tile-stream-distance',
        metavar='N',
        type=float,
        help='Set tile streaming distance (large maps only)')
    args.add_argument( # actor active distance
        '--actor-active-distance',
        metavar='N',
        type=float,
        help='Set actor active distance (large maps only)')

    if len(sys.argv) < 2:
        raise RuntimeError(args.format_help())

    args = args.parse_args()
    if  args.default:
        args.rendering      = True
        args.delta_seconds  = 0.9
        args.weather        = 'Default'
        args.no_sync        = True

    return args

def load_world(_args, _client):
    if _args.map is not None:
        print_info(f"Load Map: {BOLD}{ITALIC}{_args.map}{RESET}")
        print_end()
        world = _client.load_world(_args.map)
    elif _args.reload_map:
        print_info(f"Reload Map")
        print_end()
        world = _client.reload_world()
    elif _args.xodr_path is not None:
        if os.path.exists(_args.xodr_path):
            with open(_args.xodr_path, encoding='utf-8') as od_file:
                try:
                    data = od_file.read()
                except OSError:
                    raise OSError(f"File could not be reached. Xodr_Path:{_args.xodr_path}")
            print(f"load opendrive map {os.path.basename(_args.xodr_path)}")
            vertex_distance = 2.0   # meter
            max_road_length = 500.0 # meter
            wall_height     = 1.0   # meter
            extra_width     = 0.6   # meter
            world = _client.generate_opendrive_world(
                data,
                carla.OpendriveGenerationParameters(
                    vertex_distance         = vertex_distance,
                    max_road_length         = max_road_length,
                    wall_height             = wall_height,
                    additional_width        = extra_width,
                    smooth_junctions        = False,
                    enable_mesh_visibility  = False
                )
            )
        else:
            print_failure(f"File not found. Xodr_Path:{_args.xodr_path}")
    elif _args.osm_path is not None:
        if os.path.exists(_args.osm_path):
            with open(_args.osm_path, encoding='utf-8') as od_file:
                try:
                    data = od_file.read()
                except OSError:
                    raise OSError(f"File could not be reached. OSM_Path:{_args.xodr_path}")
            print_info('Converting OSM data to opendrive')
            print_end()
            xodr_data = carla.Osm2Odr.convert(data)
            print_info('load opendrive map.')
            print_end()
            vertex_distance = 2.0   # in meters
            max_road_length = 500.0 # in meters
            wall_height     = 0.0   # in meters
            extra_width     = 0.6   # in meters
            world = _client.generate_opendrive_world(
                xodr_data,
                carla.OpendriveGenerationParameters(
                    vertex_distance         = vertex_distance,
                    max_road_length         = max_road_length,
                    wall_height             = wall_height,
                    additional_width        = extra_width,
                    smooth_junctions        = True,
                    enable_mesh_visibility  = True
                )
            )
        else:
            print('file not found.')
    else:
        world = _client.get_world()
    
    return world

def load_graphic_options(_args, _settings):
    if _args.no_rendering:
        print_info("Disable rendering.")
        print_end()
        _settings.no_rendering_mode = True
    elif _args.rendering:
        print_info("Enable rendering.")
        print_end()
        _settings.no_rendering_mode = False
    
    if _args.no_sync:
        print_info("Disable synchronous mode.")
        print_end()
        _settings.synchronous_mode = False
    
    if _args.delta_seconds is not None:
        _settings.fixed_data_seconds = _args.delta_seconds
    elif _args.fps is not None:
        _settings.fixed_delta_seconds = (1.0 / _args.fps) if _args.fps > 0.0 else 0.0
    
    if _args.delta_seconds is not None or _args.fps is not None:
        if _settings.fixed_delta_seconds > 0.0:
            print_info('Set fixed frame rate %.2f milliseconds (%d FPS)' % (
                1000.0 * _settings.fixed_delta_seconds,
                1.0 / _settings.fixed_delta_seconds))
            print_end()
        else:
            print_info('Set variable frame rate.')
            print_end()
  
    if _args.tile_stream_distance is not None:
        _settings.tile_stream_distance = _args.tile_stream_distance
    if _args.actor_active_distance is not None:
        _settings.actor_active_distance = _args.actor_active_distance

    return _settings

def load_weather_options(_args, _world):
    if _args.weather is not None:
        if not hasattr(carla.WeatherParameters, _args.weather):
            print_failure(f"Weather preset {_args.weather} not found.")
        else:
            print_success(f"Set weather preset {_args.weather}")
            _world.set_weather(getattr(carla.WeatherParameters, _args.weather))
    return _world

# ------------------------------------------------------
# Main function
def main():
    args = load_args()

    client = carla.Client(
        args.host,
        args.port,
        worker_threads=WORKER_THREADS
    )
    client.set_timeout(CLIENT_TIMEOUT)

    world = load_world(args, client)
    settings = world.get_settings()

    settings = load_graphic_options(args, settings)
    world.apply_settings(settings)

    world = load_graphic_options(args, world)
    world = load_weather_options(args, world)

    if args.inspect:
        inspect(args, client)
    if args.list:
        list_options(client)
    if args.list_blueprints:
        list_blueprints(world. args.list_blueprints)

# ------------------------------------------------------
# Main Launcher & Exception handling
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_info("Program will be terminated because of User Interrupt. Good Bye!")
        print_end()
    except Exception as exception:
        print_failure("Program failed by an exception. Error message is:")
        print_term_size_line()
        print(ITALIC, exception, RESET)
        print_term_size_line()
        print_end()
