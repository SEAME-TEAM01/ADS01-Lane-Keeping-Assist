import pygame
import numpy as np
import cv2
import carla


client = carla.Client('localhost', 3000)
client.set_timeout(2.0)

world = client.get_world()

# プレイヤー車を生成
blueprint_library = world.get_blueprint_library()
vehicle_bp = blueprint_library.filter('vehicle.tesla.model3')[0]
vehicle_transform = carla.Transform(carla.Location(x=100, y=200, z=40), carla.Rotation(yaw=180))
vehicle = world.spawn_actor(vehicle_bp, vehicle_transform)

# スクリーンの設定
pygame.init()
display = pygame.display.set_mode((800, 600))

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


finally:
    pygame.quit()
