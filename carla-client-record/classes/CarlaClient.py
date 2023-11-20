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
# CarlaClient Class
class   CarlaClient(ABC):
    def __init__(self, args, config):
        """client, client-timeout, world, and map as args and configs"""
        self.config = config
        self.client = carla.Client(args.host, args.port)
        self.client.set_timeout(self.config.CLIENT_TIMEOUT)
        self.world = self.client.load_world(self.config.CARLA_TOWN)
        self.map = self.world.get_map()

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def launch(self) -> None:
        pass