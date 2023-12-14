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

  lane_y_min = min(left_lane['y'].min(), right_lane['y'].min())
  y_vals = np.arange(lane_y_min, height, 1)
  ideal_path_x = (ideal_path[0] * y_vals ** 2 + ideal_path[1] * y_vals + ideal_path[2]).astype(np.int32)

  ideal_path = list(zip(ideal_path_x, y_vals))

  return ideal_path

def pure_pursuit(reference_path=None, width=512, height=256):
  """
  Calculates the steering angle based on the reference path
  """

  if reference_path is None:
    return None

  vehicle_position = (width // 2, height * 1.3)
  lookahead_distance = 150

  lookahead_point = None
  
  for point in reversed(reference_path):
    distance = vehicle_position[1] - point[1]
    if  distance >= lookahead_distance:
      lookahead_point = point
      break
  
  if lookahead_point is None:
    return None

  angle_to_lookahead_radian = np.arctan2(vehicle_position[1] - lookahead_point[1], lookahead_point[0] - vehicle_position[0])
  
  return angle_to_lookahead_radian


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


def display_heading_line(image, left_lane, right_lane, steering_angle, frame):
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
    # plt.imshow(image_with_line)
    # plt.show()

def display_mask(image, mask, frame):
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
  plt.savefig(f'mask/{frame}.png')  # Save the figure to a file

def plot_heading_line(image, steering_angle, width=512, height=256, frame=1):
  center_x, center_y = width // 2, height
  line_length = height // 3
  end_x = int(center_x + line_length * np.cos(steering_angle))
  end_y = int(center_y - line_length * np.sin(steering_angle))
  image = cv2.line(image, (center_x, center_y), (end_x, end_y), (0, 255, 0), 2)
  cv2.imwrite(f'pred_out/{frame}.png', image)


def plot_lines(image, left_lane, right_lane, path_points, plot=False):
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
    image = image.numpy()
    if image.dtype != np.uint8:
      image = (image * 255).astype(np.uint8)
    for x, y in zip(left_lane['x'], left_lane['y']):
        image = cv2.circle(image, (x, y), radius=1, color=(255, 0, 0), thickness=2)
    for x, y in zip(right_lane['x'], right_lane['y']):
        image = cv2.circle(image, (x, y), radius=1, color=(0, 0, 255), thickness=2)

    for x, y in path_points[::10]:
        image = cv2.circle(image, (x, y), radius=5, color=(0, 255, 0), thickness=2)
    if (plot):
      plt.show()
    return  image


def predict_steering_angle(image, model=None, frame=1):
  """
  Predict Steering Angle from Live Image
  """
  try:
    img = tf.expand_dims(image, 0)
    pred_mask = model.predict(img)
    mask = create_mask(pred_mask)
    # display_mask(image, mask, frame)
    lanes_coords = mask_to_coordinates(mask)
    df_lanes = HDBSCAN_cluster(lanes_coords)
    # visualize_cluster(df_lanes)
    left_lane, right_lane = extract_current_lanes(df_lanes=df_lanes)
    # draw_lanes(left_lane=left_lane, right_lane=right_lane)
    path_points = calculate_ideal_path(left_lane=left_lane, right_lane=right_lane)
    steering_angle = pure_pursuit(reference_path=path_points, width=512, height=256)
    # image = plot_lines(image, left_lane, right_lane, path_points)
    # plot_heading_line(image, steering_angle, frame=frame)
    
    steering_angle = np.pi - steering_angle
    normalized_angle = (2 * steering_angle / np.pi) - 1
    print('steering_radian:', steering_angle)
    print('steering:', normalized_angle)
  except Exception as e:
    print(e)
    normalized_angle = -2
  return normalized_angle

# def main():
#   Lane = LaneDataset(train=True)
#   SAMPLE_IMAGES = Lane.X_train
#   model = keras.models.load_model(os.getenv('MODEL_PATH'), custom_objects={'dice_coef': dice_coef, 'dice_loss': dice_loss})
#   for img in SAMPLE_IMAGES.take(10):
#     predict_steering_angle(img, model)

# if __name__ == '__main__':
#   main()
