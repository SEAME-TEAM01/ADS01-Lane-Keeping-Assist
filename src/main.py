import pygame
import carla
from carla_class.HUD import HUD
from carla_class.World import World

HOST = 'localhost'
PORT = 2000

def main():
  pygame.init()
  pygame.font.init()
  world = None

  try:
    client = carla.Client(HOST, PORT)
    client.set_timeout(2.0)

    display = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)
    hud = HUD(800, 600)
    world = World(client.get_world(), hud, "vehicle.*")
    

    clock = pygame.time.Clock()
    while True:
        clock.tick_busy_loop(60)
        world.tick(clock)
        world.render(display)
        pygame.display.flip()    
    

  finally:
    if world is not None:
        world.destroy()

    pygame.quit()


if __name__ == '__main__':
    main()
