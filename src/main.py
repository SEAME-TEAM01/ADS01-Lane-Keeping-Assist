import os
import shutil
import pygame
import carla
import numpy as np
from carla_class.HUD import HUD
import matplotlib.pyplot as plt
import tensorflow as tf
import tensorflow.keras as keras
from focal_loss import BinaryFocalLoss
from multiprocessing import Process, Queue
from carla_class.World import World
from predict import predict_steering_angle
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from loss import dice_coef, dice_loss
load_dotenv('.env')

HOST = 'localhost'
PORT = 2000

class Control(object):
    def __init__(self, steering_queue) -> None:
        self.steering_queue = steering_queue
        self._control = carla.VehicleControl()
        self.frame = 1
        self._prev_steering_angle = 0
        self.model = keras.models.load_model(os.getenv('MODEL_PATH'), custom_objects={'dice_coef': dice_coef, 'BinaryFocalLoss': BinaryFocalLoss})
        # self.model = keras.models.load_model(os.getenv('MODEL_PATH'), custom_objects={'dice_coef': dice_coef, 'dice_loss': dice_loss})

    def preprocess(self, path):
        img = tf.io.read_file(path)
        os.remove(path)
        img = tf.image.decode_jpeg(img, channels=3) 
        img = tf.image.convert_image_dtype(img, tf.float32)
        img = tf.image.resize(img, [256, 512], method='nearest')
        return img
    
    def stabilize_steering_angle(self, curr_steering_angle, new_steering_angle, max_angle_deviation_two_lines=0.08):
        max_angle_deviation = max_angle_deviation_two_lines

        angle_deviation = new_steering_angle - curr_steering_angle
        if abs(angle_deviation) > max_angle_deviation:
            stabilized_steering_angle = curr_steering_angle + max_angle_deviation * np.sign(angle_deviation)
        else:
            stabilized_steering_angle = new_steering_angle

        return stabilized_steering_angle
    
    def predict(self,image):
        steer_angle = predict_steering_angle(image=image, model=self.model, frame=self.frame)
        # print('frame:', self.frame)
        self.frame += 1
        if steer_angle != -2:
            steer_angle = self.stabilize_steering_angle(self._prev_steering_angle, steer_angle)
            self._prev_steering_angle = steer_angle
        else:
            steer_angle = self._prev_steering_angle
            

        self.steering_queue.put(steer_angle)            
        
def run_world(steering_queue, img_queue):
    pygame.init()
    pygame.font.init()
    try:
        client = carla.Client(HOST, PORT)
        client.set_timeout(2.0)
        settings = client.get_world().get_settings()
        settings.fixed_delta_seconds = 1.0 / 50
        client.get_world().apply_settings(settings)
        display = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)
        hud = HUD(800, 600)
        world = World(client.get_world(), hud, 'vehicle.mercedes.coupe_2020', img_queue)
        clock = pygame.time.Clock()
        control = carla.VehicleControl()
        while True:
            if steering_queue.empty() == False:
                steering_angle = steering_queue.get()
                control.steer = steering_angle
                control.throttle = 0.4
                control.brake = 0.0
                world.player.apply_control(control)
            clock.tick_busy_loop(35)
            world.tick(clock)
            world.render(display)
            pygame.display.flip()
    finally:
        pass

def run_control(steering_queue, img_queue):
    
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)
    
    controler = Control(steering_queue)
    try:
        while True:
            if img_queue.empty() == False:
                with tf.device('/GPU:0'):
                    path = img_queue.get()
                    image = controler.preprocess(path)
                    controler.predict(image)
    finally:
        pass

def main():  
  try:
    steering_queue = Queue(maxsize=8)
    img_queue = Queue(maxsize=8)
    world_process = Process(target=run_world, args=(steering_queue, img_queue))
    control_process = Process(target=run_control, args=(steering_queue, img_queue))
    
    world_process.start()
    control_process.start()
    
    
    world_process.join()
    control_process.join()
  finally:
      pygame.quit()
      shutil.rmtree('_out')
      if world_process.is_alive():
          world_process.terminate()
      if control_process.is_alive():
          control_process.terminate()

if __name__ == '__main__':
    main()
