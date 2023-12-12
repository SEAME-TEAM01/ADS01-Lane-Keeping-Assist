# ------------------------------------------------------
# Import library
import  sys
import  configs as config

from    abc \
        import  ABC, abstractmethod
from    utils.prints \
        import  *

# ------------------------------------------------------
# Find carla library
try:
    sys.path.append(config.CARLA_DIR)
    import  carla
except  IndexError:
    print_failure("Failed to import carla egg file.")

# ------------------------------------------------------
# CarlaClient Class
class   CarlaClient(ABC):
    def __init__(self, args):
        """client, client-timeout, world, and map as args and configs"""
        self.args = args

        self.client = carla.Client(self.args.host, self.args.port)
        self.client.set_timeout(config.CLIENT_TIMEOUT)
        self.world = self.client.load_world(config.CARLA_TOWN)
        self.world.unload_map_layer(carla.MapLayer.Buildings)
        self.world.unload_map_layer(carla.MapLayer.Decals)
        self.world.unload_map_layer(carla.MapLayer.Foliage)
        self.world.unload_map_layer(carla.MapLayer.ParkedVehicles)
        self.world.unload_map_layer(carla.MapLayer.Particles)
        self.world.unload_map_layer(carla.MapLayer.Ground)
        self.world.unload_map_layer(carla.MapLayer.Props)
        self.world.unload_map_layer(carla.MapLayer.StreetLights)

        self.map = self.world.get_map()

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def launch(self) -> None:
        pass