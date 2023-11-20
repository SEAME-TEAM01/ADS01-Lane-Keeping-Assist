# ------------------------------------------------------
# Import Base Library
import  logging
from    util.prints \
        import  *

# ------------------------------------------------------
# Log Settings
def log_setting(args):
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)