import pygame
import carla
from carla_class.HUD import HUD
from carla_class.World import World
# from predict import predict
import matplotlib.pyplot as plt

HOST = 'localhost'
PORT = 2000
MODEL_PATH = ""

class Control(object):
    def __init__(self, world) -> None:
        self._control = carla.VehicleControl()
        self._world = world

    def control(self, steering, throttle):
        self._control.steer = steering
        self._control.throttle = throttle
        self._control.brake = 0.0

        self._world.player.apply_control(self._control)
        
    def predict(self,image):
        plt.imshow(image)
        plt.show()
        # steer_angle = predict(image=image, model=MODEL_PATH)
        # self.control(steering=steer_angle, throttle=0.3)

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
    controler = Control(world)

    clock = pygame.time.Clock()
    while True:
        clock.tick_busy_loop(60)
        world.tick(clock)
        world.render(display)
        if world.img_queue.empty() == False:
            image = world.img_queue.get()
            controler.predict(image)
        pygame.display.flip()

  finally:
    if world is not None:
        world.destroy()

    pygame.quit()


if __name__ == '__main__':
    main()
