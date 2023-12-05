import pygame
import carla

HOST = 'localhost'
PORT = 3000

def main():
  pygame.init()
  pygame.font.init()
  world = None

  try:
    client = carla.Client(HOST, PORT)
    client.set_timeout(2.0)

    display = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)
  finally:
     pass

if __name__ == '__main__':
    main()
