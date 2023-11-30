# ------------------------------------------------------
# Import custom library
import  configs as config
from    utils.colors \
        import  *
from    utils.prints \
        import  *
from    utils.args \
        import  load_args
from    classes.CarlaDataRecorder \
        import  CarlaDataRecorder

# ------------------------------------------------------
# Import Library
try:
    import  logging
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
# Main function
def main():
    args = load_args()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

    try:
        lanes =[deque(maxlen=config.number_of_lanepoints), 
                deque(maxlen=config.number_of_lanepoints), 
                deque(maxlen=config.number_of_lanepoints), 
                deque(maxlen=config.number_of_lanepoints)]
        game = CarlaDataRecorder(args, lanes)
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
