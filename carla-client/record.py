#!/usr/bin/env python

# ------------------------------------------------------
# Goal for this main.py
# - Simpler map
# - Manual Driving System

# __doc__ :
"""
Use ARROWS or WASD keys for control.

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
# Import Util Libraries
from    util.colors \
        import  *
from    util.prints \
        import  *
from    util.variables \
        import  *
from    util.utils \
        import  *

# ------------------------------------------------------
# Import Libraries
try:
    import  os
    import  re
    import  sys
    import  glob
    import  math
    import  numpy
    import  pygame
    import  random
    import  weakref
    import  datetime
    import  collections
except  ImportError as exception:
    print_failure("Failed to load some libraries. Check all packages installed properly.")
    print_failure("Exception message is:")
    print_term_size_line()
    print(ITALIC, exception, RESET)
    print_term_size_line()
    print_end()

# ------------------------------------------------------
# Find carla library
try:
    sys.path.append(glob.glob("../carla/dist/carla-*%d.%d-%s.egg" % (
        sys.version_info.major,
        sys.version_info.minor,
        "win-amd64" if os.name == "nt" else "linux-x86_64"))[0])
except  IndexError:
    pass
import  carla

# ------------------------------------------------------
# Import Features
from    settings.args \
        import  load_args_record
from    settings.logs \
        import  log_setting
from    settings.gets \
        import  *
from    classes.HUD \
        import  HUD
from    classes.World \
        import  World
from    classes.KeyboardControl \
        import  KeyboardControl

# ------------------------------------------------------
# Game Loop
def game_init():
    pygame.init()
    pygame.font.init()

def loop(args):
    game_init()
    world = None
    original_settings = None

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(RECORD_CLIENT_TIMEOUT)
        sim_world = client.load_world('Town03_Opt', carla.MapLayer.Walls)
        sim_world.unload_map_layer(carla.MapLayer.Buildings)
        sim_world.unload_map_layer(carla.MapLayer.Decals)
        sim_world.unload_map_layer(carla.MapLayer.Foliage)
        sim_world.unload_map_layer(carla.MapLayer.ParkedVehicles)
        sim_world.unload_map_layer(carla.MapLayer.Particles)
        sim_world.unload_map_layer(carla.MapLayer.Ground)
        sim_world.unload_map_layer(carla.MapLayer.Props)
        sim_world.unload_map_layer(carla.MapLayer.StreetLights)

        if args.sync:
            original_settings = sim_world.get_settings()
            settings = sim_world.get_settings()
            if not settings.synchronous_mode:
                settings.synchronous_mode = True
                settings.fixed_delta_seconds = 0.05
            sim_world.apply_settings(settings)
        
        if args.autopilot and not sim_world.get_settings().synchronous_mode:
            print_warning("You are currently in asynchronous mode.")
            print_warning("Could experience some issues with the traffic simulation.", is_first_line=False)
            print_end()
        
        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        display.fill((0,0,0))
        pygame.display.flip()

        hud         = HUD(args.width, args.height, __doc__)
        world       = World(sim_world, hud, args)
        world.camera_manager.toggle_camera()
        controller  = KeyboardControl(world, args.autopilot)

        if args.sync:   sim_world.tick()
        else:           sim_world.wait_for_tick()

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
        if world and world.recording_enabled:
            client.stop_recorder()
        if world is not None:
            world.destroy()
        pygame.quit()
        print_info("Main loop destructor has finished")
        print_end()

# ------------------------------------------------------
# Main function
def main():
    args = load_args_record()
    log_setting(args)

    try:
        loop(args)
    except KeyboardInterrupt:
        raise KeyboardInterrupt("")

# ------------------------------------------------------
# Main Launcher & Exception handling
if  __name__ == "__main__":
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
