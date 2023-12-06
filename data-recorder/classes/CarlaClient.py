# ------------------------------------------------------
# Import library
import  os
import  sys
import  glob
from    abc \
        import  ABC, abstractmethod

import  configs as config

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
    def __init__(self, args):
        """client, client-timeout, world, and map as args and configs"""
        self.args = args

        self.client = carla.Client(self.args.host, self.args.port)
        self.client.set_timeout(config.CLIENT_TIMEOUT)
        self.world = self.client.load_world(config.CARLA_TOWN)
        # self.world.unload_map_layer(carla.MapLayer.Buildings)
        # self.world.unload_map_layer(carla.MapLayer.Decals)
        # self.world.unload_map_layer(carla.MapLayer.Foliage)
        # self.world.unload_map_layer(carla.MapLayer.ParkedVehicles)
        # self.world.unload_map_layer(carla.MapLayer.Particles)
        # self.world.unload_map_layer(carla.MapLayer.Ground)
        # self.world.unload_map_layer(carla.MapLayer.Props)
        # self.world.unload_map_layer(carla.MapLayer.StreetLights)

        self.map = self.world.get_map()

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def launch(self) -> None:
        pass