# ------------------------------------------------------
# Import Util Libraries
from    util.colors \
        import  *
from    util.prints \
        import  *
from    util.configs \
        import  *
from    util.utils \
        import  *

# ------------------------------------------------------
# Import Libraries
try:
    import  os
    import  sys
    import  glob
    from    collections \
            import  deque
    import  traceback
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
from    classes.CarlaGame \
        import  CarlaGame


# ------------------------------------------------------
# Main function
def main():
    config = Configs()
    args = load_args_record()
    log_setting(args)

    try:
        lanes =[deque(maxlen=config.number_of_lanepoints), 
                deque(maxlen=config.number_of_lanepoints), 
                deque(maxlen=config.number_of_lanepoints), 
                deque(maxlen=config.number_of_lanepoints)]
        print_debug("DEBUG main() - after lane def")
        game = CarlaGame(args, config, lanes)
        game.launch()
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
        print()
        print(ITALIC, traceback.format_exc(), RESET)
        print_term_size_line()
        print_end()
