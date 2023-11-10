#!/usr/bin/env python

# ------------------------------------------------------
# Goal for this main.py
# - Dynamic Weather
# - Autonomous Driving
# - Recording Data

"""
CARLA: Dynamic Weather (DW) & Manual Driving System (MDS)

This subject is combined with `dynamic_weather.py` and `manual_control.py` in Carla's official examples.

DYNAMIC WEATHER INFORMATION
    Connect to a CARLA Simulator instance and control the weather. Change Sun
    position smoothly with time and generate storms occasionally.

MANUAL DRIVING INFORMATION
    W            : throttle
    S            : brake
    A/D          : steer left/right
    Q            : toggle reverse
    Space        : hand-brake
    P            : toggle autopilot
    M            : toggle manual transmission
    ,/.          : gear up/down
    CTRL + W     : toggle constant velocity mode at 60 km/h

    L            : toggle next light type
    SHIFT + L    : toggle high beam
    Z/X          : toggle right/left blinker
    I            : toggle interior light

    TAB          : change sensor position
    ` or N       : next sensor
    [1-9]        : change to sensor [1-9]
    G            : toggle radar visualization
    C            : change weather (Shift+C reverse)
    Backspace    : change vehicle

    O            : open/close all doors of vehicle
    T            : toggle vehicle's telemetry

    V            : Select next map layer (Shift+V reverse)
    B            : Load current selected map layer (Shift+B to unload)

    R            : toggle recording images to disk

    CTRL + R     : toggle recording of simulation (replacing any previous)
    CTRL + P     : start replaying last recorded simulation
    CTRL + +     : increments the start time of the replay by 1 second (+SHIFT = 10 seconds)
    CTRL + -     : decrements the start time of the replay by 1 second (+SHIFT = 10 seconds)

    F1           : toggle HUD
    H/?          : toggle help
    ESC          : quit

"""

# ------------------------------------------------------
# Import base library
import  os
import  re
import  sys
import  glob
import  math
import  time
import  random
import  logging
import  weakref
import  argparse
import  collections
import  datetime
import  pygame

from    pygame.locals   import  KMOD_CTRL, \
                                KMOD_SHIFT, \
                                K_0, \
                                K_9, \
                                K_BACKQUOTE, \
                                K_BACKSPACE, \
                                K_COMMA, \
                                K_DOWN, \
                                K_ESCAPE, \
                                K_F1, \
                                K_LEFT, \
                                K_PERIOD, \
                                K_RIGHT, \
                                K_SLASH, \
                                K_SPACE, \
                                K_TAB, \
                                K_UP, \
                                K_a, \
                                K_b, \
                                K_c, \
                                K_d, \
                                K_e, \
                                K_f, \
                                K_g, \
                                K_h, \
                                K_i, \
                                K_l, \
                                K_m, \
                                K_n, \
                                K_o, \
                                K_p, \
                                K_q, \
                                K_r, \
                                K_s, \
                                K_t, \
                                K_v, \
                                K_w, \
                                K_x, \
                                K_z, \
                                K_MINUS, \
                                K_EQUALS
                                

# ------------------------------------------------------
# Find Carla module
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import  carla

# ------------------------------------------------------
# WEATHER
def clamp(value, _min=0.0, _max=100.0):
    return max(_min, min(value, _max))

class Sun(object):
    def __init__(self, azimuth, altitude):
        self.azimuth = azimuth
        self.altitude = altitude
        self._t = 0.0

    def tick(self, delta_seconds):
        self._t += 0.008 * delta_seconds
        self._t %= 2.0 * math.pi
        self.azimuth += 0.25 * delta_seconds
        self.azimuth %= 360.0
        self.altitude = (70 * math.sin(self._t)) - 20

    def __str__(self):
        return 'Sun(alt: %.2f, azm: %.2f)' % (self.altitude, self.azimuth)

class Storm(object):
    def __init__(self, precipitation):
        self._t = precipitation if precipitation > 0.0 else -50.0
        self._increasing = True
        self.clouds = 0.0
        self.rain = 0.0
        self.wetness = 0.0
        self.puddles = 0.0
        self.wind = 0.0
        self.fog = 0.0

    def tick(self, delta_seconds):
        delta = (1.3 if self._increasing else -1.3) * delta_seconds
        self._t = clamp(delta + self._t, -250.0, 100.0)
        self.clouds = clamp(self._t + 40.0, 0.0, 90.0)
        self.rain = clamp(self._t, 0.0, 80.0)
        delay = -10.0 if self._increasing else 90.0
        self.puddles = clamp(self._t + delay, 0.0, 85.0)
        self.wetness = clamp(self._t * 5, 0.0, 100.0)
        self.wind = 5.0 if self.clouds <= 20 else 90 if self.clouds >= 70 else 40
        self.fog = clamp(self._t - 10, 0.0, 30.0)
        if self._t == -250.0:
            self._increasing = True
        if self._t == 100.0:
            self._increasing = False

    def __str__(self):
        return 'Storm(clouds=%d%%, rain=%d%%, wind=%d%%)' % (self.clouds, self.rain, self.wind)

class Weather(object):
    def __init__(self, weather):
        self.weather = weather
        self._sun = Sun(weather.sun_azimuth_angle, weather.sun_altitude_angle)
        self._storm = Storm(weather.precipitation)

    def tick(self, delta_seconds):
        self._sun.tick(delta_seconds)
        self._storm.tick(delta_seconds)
        self.weather.cloudiness = self._storm.clouds
        self.weather.precipitation = self._storm.rain
        self.weather.precipitation_deposits = self._storm.puddles
        self.weather.wind_intensity = self._storm.wind
        self.weather.fog_density = self._storm.fog
        self.weather.wetness = self._storm.wetness
        self.weather.sun_azimuth_angle = self._sun.azimuth
        self.weather.sun_altitude_angle = self._sun.altitude

    def __str__(self):
    
        return '%s %s' % (self._sun, self._storm)

# 
# DRIVING SYSTEM
def game_loop(args):
    pygame.init()

    pygame.init()
    pygame.font.init()
    world = None
    original_settings = None

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(2000.0)

        sim_world = client.get_world()
        if args.sync:
            original_settings = sim_world.get_settings()
            settings = sim_world.get_settings()
            if not settings.synchronous_mode:
                settings.synchronous_mode = True
                settings.fixed_delta_seconds = 0.05
            sim_world.apply_settings(settings)

            traffic_manager = client.get_trafficmanager()
            traffic_manager.set_synchronous_mode(True)

        if args.autopilot and not sim_world.get_settings().synchronous_mode:
            print("WARNING: You are currently in asynchronous mode and could "
                  "experience some issues with the traffic simulation")

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)
        display.fill((0,0,0))
        pygame.display.flip()

        hud = HUD(args.width, args.height)
        world = World(sim_world, hud, args)
        controller = KeyboardControl(world, args.autopilot)

        if args.sync:
            sim_world.tick()
        else:
            sim_world.wait_for_tick()

        clock = pygame.time.Clock()
        while True:
            if args.sync:
                sim_world.tick()
            clock.tick_busy_loop(60)
            if controller.parse_events(client, world, clock, args.sync):
                return
            world.tick(clock)
            world.render(display)
            pygame.display.flip()

    finally:

        if original_settings:
            sim_world.apply_settings(original_settings)

        if (world and world.recording_enabled):
            client.stop_recorder()

        if world is not None:
            world.destroy()

        pygame.quit()

# ------------------------------------------------------
# UTIL
def args_generator():
    arg = argparse.ArgumentParser(description=__doc__)
   
    # base args
    arg.add_argument( # host
        "--host",
        metavar = 'H',
        default = '126.0.0.1',
        help    = 'IP of the host server (default: 127.0.0.1)'
    )
    arg.add_argument( # port
        '-p', '--port',
        metavar = 'P',
        default = 2000,
        type    = int,
        help    = 'TCP port to listen to (default: 2000)'
    )

    # weather args
    arg.add_argument( # weather speed
        '-s', '--speed',
        metavar = 'FACTOR',
        default = 1.0,
        type    = float,
        help    = 'rate at which the weather changes (default: 1.0)'
    )

    # manual args
    arg.add_argument( # debugging
        '-v', '--verbose',
        action  = 'store_true',
        dest    = 'debug',
        help    = 'print debug information'
    )
    # arg.add_argument( # autopilot
    #     '-a', '--autopilot',
    #     action  = 'store_true',
    #     default = True
    #     help    = 'enable autopilot'
    # )
    arg.add_argument( # resolution
        '--res',
        metavar = 'WIDTHxHEIGHT',
        default = '1280x720',
        help    = 'window resolution (default: 1280x720)'
    )
    arg.add_argument( # filter
        '--filter',
        metavar = 'PATTERN',
        default = 'vehicle.*',
        help    = 'actor filter (default: "vehicle.*")'
    )
    arg.add_argument( # actor generation
        '--generation',
        metavar = 'G',
        default = '2',
        help    = 'restrict to certain actor generation (values: "1","2","All" - default: "2")'
    )
    arg.add_argument( # actor role name
        '--rolename',
        metavar = 'NAME',
        default = 'hero',
        help    = 'actor role name (default: "hero")'
    )
    arg.add_argument( # gamma
        '--gamma',
        default = 2.2,
        type    = float,
        help    = 'Gamma correction of the camera (default: 2.2)'
    )
    arg.add_argument( # synchronous mode activation
        '--sync',
        action  = 'store_true',
        help    = 'Activate synchronous mode execution'
    )
    
    # arg parse
    args = arg.parse_args()
    args.width, args.height = [int(x) for x in args.res.split('x')]

    # return args
    return args

def log_setting(_debug, _host, _port):
    log_level = logging.DEBUG if _debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)
    logging.info('listening to server %s:%s', _host, _port)
    print(__doc__)

# ------------------------------------------------------
# MAIN
def loop(args):
    game_loop()


def main():
    args = args_generator()
    log_setting(args.debug, args.host, args.port)

    try:
        loop(args)
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')

if __name__ == '__main__':
    main()
