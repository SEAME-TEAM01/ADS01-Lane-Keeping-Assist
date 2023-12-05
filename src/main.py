import pygame
import carla
from carla_class.HUD import HUD
from carla_class.World import World

HOST = 'localhost'
PORT = 2000

class Control(object):
    def __init__(self, world) -> None:
        self._control = carla.VehicleControl()
        self._world = world

    def control(self, steering, throttle):
        self._control.steer = steering
        self._control.throttle = throttle
        self._control.brake = 0.0

        self._world.player.apply_control(self._control)


def main():
  pygame.init()
  pygame.font.init()
  world = None

  try:
    client = carla.Client(HOST, PORT)
    client.set_timeout(2.0)
    settings = client.get_world().get_settings()
    settings.fixed_delta_seconds = 0.05  # (1/20 = 0.05sec)

    display = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)
    hud = HUD(800, 600)
    world = World(client.get_world(), hud, "vehicle.*")
    world.add_camera_to_vehicle()
    controler = Control(world)

    clock = pygame.time.Clock()
    while True:
        clock.tick_busy_loop(60)
        world.tick(clock)
        world.render(display)
        controler.control(steering=0.0, throttle=0.5)
        pygame.display.flip()

  finally:
    if world is not None:
        world.destroy()

    pygame.quit()


if __name__ == '__main__':
    main()
