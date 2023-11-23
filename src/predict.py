import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import tensorflow.keras as keras
from loss import dice_coef, dice_loss
from dataset import LaneDataset
from dotenv import load_dotenv
load_dotenv('.env')

Lane = LaneDataset(train=False)
SAMPLE_IMAGES = Lane.X_train

model = keras.models.load_model(os.getenv('MODEL_PATH'), custom_objects={'dice_coef': dice_coef, 'dice_loss': dice_loss})

def create_mask(pred_mask):
    mask = pred_mask[..., -1] >= 0.5
    pred_mask[..., -1] = tf.where(mask, 1, 0)
    return pred_mask[0]

def extract_current_lanes(pred_mask):
    """
    Extracts the current lanes from the predicted mask
    """
    return pred_mask


def calculate_steer_angle():
    """
    Calculates the steering angle based on the predicted mask
    """

def mask_to_coordinates(mask):
    """
    Converts the predicted mask to coordinates
    """
    mask = np.squeeze(mask, axis=-1)
    mask = mask == 1

    y, x = np.where(mask)
    coords = list(zip(x, y))
    return coords

def draw_lanes(lanes):
  """
  Draws the lanes on the image
  """
  background = np.zeros((256, 512), dtype=np.uint8)
  for x, y in lanes:
    background[y, x] = 255
  plt.imshow(background)
  plt.show()

  return background


def predict(image):
    """
    Predicts the current lane and steering angle
    """
    for img in image.take(1):
      img = tf.expand_dims(img, 0)
      pred_mask = model.predict(img)
      mask = create_mask(pred_mask)
      lanes = mask_to_coordinates(mask)
      curr_lanes = extract_current_lanes(mask)

np.set_printoptions(threshold=np.inf)
predict(SAMPLE_IMAGES)
