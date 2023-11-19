from keras.models import load_model
from keras.utils import custom_object_scope
from focal_loss import BinaryFocalLoss
from loss import instance_loss
from utils import iou
import numpy as np
import matplotlib.pyplot as plt
import cv2

model_path = '/content/drive/MyDrive/ads/output/model/20231118-1700089152/lane4_lena_6_model.hdf5'

with custom_object_scope({'BinaryFocalLoss': BinaryFocalLoss, 'instance_loss': instance_loss, 'iou': iou}):
    model = load_model(model_path)

def predict(raw_img, input):
  result = model.predict(input)
  bin_output = result[0][0]
  ins_output = result[1][0]

  y_coords, x_coords = np.where(bin_output[:,:,0])
  lanes = [(x,y) for (x,y) in zip(x_coords, y_coords)]

  lanes_array = [list(point) for point in lanes]
  lanes_arr_np = np.array([lanes_array], dtype=np.int32)

  cv2.polylines(raw_img, lanes_arr_np, isClosed=False, color=(0, 255, 0), thickness=5)

  plt.imshow(raw_img)
  plt.show()
