# ------------------------------------------------------
# Import base library
import  os
import  sys
import  glob
import  math
import  pygame
import  datetime
from    abc \
        import  ABC, abstractmethod

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
# Import Custom Libraries
import  util.configs as config

# ------------------------------------------------------
# CarlaClient Class
class   CarlaClient(ABC):
    def __init__(self, args):
        """client, client-timeout, world, and map as args and configs"""
        self.client = carla.Client(args.host, args.port)
        self.client.set_timeout(config.CLIENT_TIMEOUT)
        self.world = self.client.load_world(config.CARLA_TOWN)
        self.map = self.world.get_map()

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def launch(self) -> None:
        pass