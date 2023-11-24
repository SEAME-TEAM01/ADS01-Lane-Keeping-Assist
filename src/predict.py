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

def extract_current_lanes(lanes, img_width=512, img_height=256):
    """
    Extracts the closest left and right lane coordinates from a list of lane coordinates.

    Args:
    - lanes: List of (x, y) tuples representing lane coordinates.
    - img_width: The width of the image.
    - img_height: The height of the image.

    Returns:
    - Tuple containing two lists of coordinates, one for the closest left lane and one for the closest right lane.
    """
    center_x = img_width // 2

    closest_left_lane = [None] * img_height
    closest_right_lane = [None] * img_height

    min_left_dists = [img_width] * img_height
    min_right_dists = [img_width] * img_height

    lanes_by_y = {}
    for x, y in lanes:
        if y in lanes_by_y:
            lanes_by_y[y].append(x)
        else:
            lanes_by_y[y] = [x]

    for y in range(img_height//2, img_height):
        if y not in lanes_by_y: continue
        for x in lanes_by_y[y]:
            if x < center_x:
                dist_to_center = center_x - x
                if dist_to_center < min_left_dists[y]:
                    min_left_dists[y] = dist_to_center
                    closest_left_lane[y] = (x, y)
            else:
                dist_to_center = x - center_x
                if dist_to_center < min_right_dists[y]:
                    min_right_dists[y] = dist_to_center
                    closest_right_lane[y] = (x, y)

    closest_left_lane = [coord for coord in closest_left_lane if coord is not None]
    closest_right_lane = [coord for coord in closest_right_lane if coord is not None]

    return closest_left_lane, closest_right_lane



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

def draw_lanes(lanes=None, left_lane=None, right_lane=None):
  """
  Draws the lanes on the image
  """
  background = np.zeros((256, 512), dtype=np.uint8)
  if (left_lane is not None) and (right_lane is not None):
    for x, y in left_lane:
      background[y, x] = 255
    for x, y in right_lane:
      background[y, x] = 255

  if (left_lane is None) and (right_lane is None):
    background = np.zeros((256, 512), dtype=np.uint8)
    for x, y in lanes:
      background[y, x] = 255
  plt.imshow(background)
  plt.show()
  return background


def test_predict(image):
    """
    Predicts the current lane and steering angle
    """
    for img in image.take(1):
      plt.imshow(img)
      plt.show()
      img = tf.expand_dims(img, 0)
      pred_mask = model.predict(img)
      mask = create_mask(pred_mask)
      lanes = mask_to_coordinates(mask)
      draw_lanes(lanes)
      curr_lanes = extract_current_lanes(lanes)
      draw_lanes(left_lane=curr_lanes[0], right_lane=curr_lanes[1])

np.set_printoptions(threshold=np.inf)
test_predict(SAMPLE_IMAGES)
