import os
import numpy as np
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
  if lanes is None:
    for x, y in zip(left_lane['x'], left_lane['y']):
      background[y, x] = 255
    for x, y in zip(right_lane['x'], right_lane['y']):
      background[y, x] = 255

  if (left_lane is None) and (right_lane is None):
    background = np.zeros((256, 512), dtype=np.uint8)
    for x, y in lanes:
      background[y, x] = 255
  plt.imshow(background)
  plt.show()
  return background


def test_predict(image, model=None):
  """

  """
  lanes = []

  for img in image.take(2):
    img = tf.expand_dims(img, 0)
    pred_mask = model.predict(img)
    mask = create_mask(pred_mask)
    lanes_coords = mask_to_coordinates(mask)
    # draw_lanes(lanes=lanes_coords)
    # curr_lanes = extract_current_lanes(lanes)
    # draw_lanes(left_lane=curr_lanes[0], right_lane=curr_lanes[1])
    lanes.append(lanes_coords)
  return lanes

def predict(image, model=None):
  """
  Predict Steering Angle from Live Image
  """
  img = tf.expand_dims(image, 0)
  pred_mask = model.predict(img)
  mask = create_mask(pred_mask)
  lanes_coords = mask_to_coordinates(mask)
  draw_lanes(lanes=lanes_coords)
  df_lanes = HDBSCAN_cluster(lanes_coords)
  left_lane, right_lane = extract_current_lanes(df_lanes=df_lanes)
  draw_lanes(left_lane=left_lane, right_lane=right_lane)

Lane = LaneDataset(train=True)
SAMPLE_IMAGES = Lane.X_train
model = keras.models.load_model(os.getenv('MODEL_PATH'), custom_objects={'dice_coef': dice_coef, 'dice_loss': dice_loss})
for img in SAMPLE_IMAGES.take(5):
  predict(img, model)
