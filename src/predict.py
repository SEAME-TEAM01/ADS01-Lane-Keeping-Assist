import os
import numpy as np
import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
import tensorflow.keras as keras
from clustering import HDBSCAN_cluster,visualize_cluster
from dotenv import load_dotenv
from loss import dice_coef, dice_loss
load_dotenv('.env')

def create_mask(pred_mask):
  mask = pred_mask[..., -1] >= 0.5
  pred_mask[..., -1] = tf.where(mask, 1, 0)
  
  # only if you drive on highway this is 
  pred_mask[0, :150, :, :] = 0
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


def display_heading_line(image, left_lane, right_lane, steering_angle):
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

    height, width = image_with_line.shape[:2]
    center_x, center_y = width // 2, height
    line_length = height // 3  # Adjust the length of the heading line as needed
    angle_radians = np.deg2rad(180 - steering_angle)  # Convert to radians

    # Calculate end point of the heading line
    end_x = int(center_x + line_length * np.cos(angle_radians))
    end_y = int(center_y - line_length * np.sin(angle_radians))

    image_with_line = cv2.line(image_with_line, (center_x, center_y), (end_x, end_y), (0, 0, 255), 3)

    plt.imshow(image_with_line)
    plt.show()

def display_mask(image, mask):
  """
  Displays the image and the mask
  """
  plt.figure(figsize=(15, 15))
  title = ['Input Image', 'Predicted Mask']
  display_list = [image, mask]
  for i in range(len(display_list)):
    plt.subplot(1, len(display_list), i+1)
    plt.title(title[i])
    plt.imshow(tf.keras.preprocessing.image.array_to_img(display_list[i]))
    plt.axis('off')
  plt.show()
  

def predict_steering_angle(image, model=None):
  """
  Predict Steering Angle from Live Image
  """
  img = tf.expand_dims(image, 0)
  pred_mask = model.predict(img)
  mask = create_mask(pred_mask)  
  # display_mask(image, mask)
  lanes_coords = mask_to_coordinates(mask)
  df_lanes = HDBSCAN_cluster(lanes_coords)
  # visualize_cluster(df_lanes)
  left_lane, right_lane = extract_current_lanes(df_lanes=df_lanes)
  # draw_lanes(left_lane=left_lane, right_lane=right_lane)
  steering_angle = calculate_steer_angle(left_lane, right_lane, width=512, height=256)
  print(steering_angle)
  # display_heading_line(image, left_lane, right_lane, steering_angle)
  return steering_angle

# def main():
#   Lane = LaneDataset(train=True)
#   SAMPLE_IMAGES = Lane.X_train
#   model = keras.models.load_model(os.getenv('MODEL_PATH'), custom_objects={'dice_coef': dice_coef, 'dice_loss': dice_loss})
#   for img in SAMPLE_IMAGES.take(10):
#     predict_steering_angle(img, model)

# if __name__ == '__main__':
#   main()
