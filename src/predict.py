import os
import math
import numpy as np
import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
import tensorflow.keras as keras
from clustering import HDBSCAN_cluster
from dataset import LaneDataset
from dotenv import load_dotenv
from loss import dice_coef, dice_loss
load_dotenv('.env')

def create_mask(pred_mask):
  mask = pred_mask[..., -1] >= 0.5
  pred_mask[..., -1] = tf.where(mask, 1, 0)
  return pred_mask[0]

def extract_current_lanes(df_lanes=None, width=512):
  """
  Extracts the current lanes from the dataframe
  """
  if df_lanes is None: return None, None

  middle = width // 2

  cluster_centroids = df_lanes.groupby('cluster')['x'].mean()

  left_ids = cluster_centroids[cluster_centroids < middle].index
  left_clusters = df_lanes[df_lanes['cluster'].isin(left_ids)]
  right_ids = cluster_centroids[cluster_centroids > middle].index
  right_clusters = df_lanes[df_lanes['cluster'].isin(right_ids)]


  left_closest_cluster = left_clusters.groupby('cluster')['x'].apply(lambda x: abs(x - middle).mean()).nsmallest(1).index
  left_lane_cluster = df_lanes[df_lanes['cluster'] == left_closest_cluster[0]]

  right_closest_cluster = right_clusters.groupby('cluster')['x'].apply(lambda x: abs(x - middle).mean()).nsmallest(1).index
  right_lane_cluster = df_lanes[df_lanes['cluster'] == right_closest_cluster[0]]

  return left_lane_cluster, right_lane_cluster

def calculate_quadratic_coefficients(lane):
    """
    Fits a quadratic polynomial to the lane points and returns the coefficients.
    """
    # Fit a 2nd degree polynomial to the lane points
    poly_fit = np.polyfit(lane['y'], lane['x'], 2)
    return poly_fit

def calculate_ideal_path(left_lane=None, right_lane=None, height=256):
  """
  Calculates the ideal path from the left and right lanes
  """
  if (left_lane is None) and (right_lane is None):
    return []

  left_fit = calculate_quadratic_coefficients(left_lane)
  right_fit = calculate_quadratic_coefficients(right_lane)

  ideal_path = (left_fit + right_fit) / 2

  lane_y_min = left_lane['y'].min()
  y_vals = np.arange(lane_y_min, height, 1)
  ideal_path_x = (ideal_path[0] * y_vals ** 2 + ideal_path[1] * y_vals + ideal_path[2]).astype(np.int32)

  ideal_path = list(zip(ideal_path_x, y_vals))

  return ideal_path


def calculate_steer_angle(left_lane=None, right_lane=None, width=512, height=256):
  """
  Calculates the steering angle based on the predicted mask
  """
  mid = width // 2
  left_mid_x = left_lane['x'].mean()
  right_mid_x = right_lane['x'].mean()

  x_offset = (left_mid_x + right_mid_x) / 2 - mid
  y_offset = int(height * 0.6)

  angle_to_mid_radian = np.arctan(x_offset / y_offset)
  angle_to_mid_deg = np.degrees(angle_to_mid_radian)
  steering_angle = angle_to_mid_deg + 90
  return steering_angle

def pure_pursuit(reference_path=None, width=512, height=256):
  """
  Calculates the steering angle based on the reference path
  """

  if reference_path is None:
    return None

  vehicle_position = (width // 2, height)
  lookahead_distance = 100 # should be dynamic based on speed

  lookahead_point = None
  for point in reversed(reference_path):
    if math.hypot(point[0] - vehicle_position[0], vehicle_position[1] - point[1]) > lookahead_distance:
      lookahead_point = point
      break

  print(lookahead_point)
  if lookahead_point is None:
    return None

  angle_to_lookahead_radian = np.arctan2(vehicle_position[1] - lookahead_point[1], lookahead_point[0] - vehicle_position[0])
  steering_angle = np.degrees(angle_to_lookahead_radian)
  steering_angle = min(max(steering_angle, 0), 180)

  return steering_angle


def mask_to_coordinates(mask):
  """
  Converts the predicted mask to coordinates
  """
  mask = np.squeeze(mask, axis=-1)
  mask = mask == 1

  y, x = np.where(mask)
  coords = list(zip(x, y))
  return coords


def display_lines(image, left_lane, right_lane, path_points):
    """
    Draws heading line on the image based on left and right lane coordinates and steering angle.

    Args:
    - image: A TensorFlow EagerTensor representing the image.
    - left_lane: Coordinates of the left lane.
    - right_lane: Coordinates of the right lane.
    - steering_angle: The calculated steering angle.

    Returns:
    - Image tensor with the heading line drawn.
    """
    image_with_line = np.copy(image)

    for x, y in zip(left_lane['x'], left_lane['y']):
      image_with_line[y, x] = 255
    for x, y in zip(right_lane['x'], right_lane['y']):
      image_with_line[y, x] = 255

    x_coords, y_coords = zip(*path_points)
    x_coords_selected = x_coords[::10]
    y_coords_selected = y_coords[::10]

    plt.plot(x_coords_selected, y_coords_selected, 'o', markersize=5, linewidth=2, color='green')
    plt.imshow(image_with_line)
    plt.show()


def predict(image, model=None):
  """
  Predict Steering Angle from Live Image
  """
  img = tf.expand_dims(image, 0)
  pred_mask = model.predict(img)
  mask = create_mask(pred_mask)
  lanes_coords = mask_to_coordinates(mask)
  df_lanes = HDBSCAN_cluster(lanes_coords)
  left_lane, right_lane = extract_current_lanes(df_lanes=df_lanes) # return dataframe x, y coordinates
  path_points = calculate_ideal_path(left_lane=left_lane, right_lane=right_lane)
  steering_angle = pure_pursuit(reference_path=path_points)
  print(steering_angle)
  display_lines(image, left_lane, right_lane, path_points)
  return steering_angle

Lane = LaneDataset(train=True)
SAMPLE_IMAGES = Lane.X_train
model = keras.models.load_model(os.getenv('MODEL_PATH'), custom_objects={'dice_coef': dice_coef, 'dice_loss': dice_loss})
for img in SAMPLE_IMAGES.take(3):
  predict(img, model)
