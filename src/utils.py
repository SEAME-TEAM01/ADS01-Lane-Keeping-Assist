from PIL import Image
import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split

def GRResize(im, size, filter):
  arr = np.array(im, dtype=np.float32) / 255.0
  arr = np.where(arr <= 0.04045, arr/12.92,((arr+0.055)/1.055)**2.4)
  arrOut = np.zeros((size[1], size[0]))
  chan = Image.fromarray(arr)
  chan.resize(size, filter)
  arrOut[:,:] = np.array(chan).clip(0.0, 1.0)
  arrOut = np.where(arrOut <= 0.0031308, 12.92*arrOut, 1.055*arrOut**(1.0/2.4)-0.055)
  arrOut = np.uint8(np.rint(arrOut*255.0))
  return Image.fromarray(arrOut)

def split_dataset(Lane: LaneDataset):
  tf.random.set_seed(40)
  return train_test_split(Lane.data, Lane.bin_label, Lane.ins_label, test_size=0.15, random_state=0)

def iou(y_true, y_pred):
    def f(y_true, y_pred):
        intersection = (y_true * y_pred).sum()
        union = y_true.sum() + y_pred.sum() - intersection
        x = (intersection + 1e-15) / (union + 1e-15)
        x = x.astype(np.float32)
        return x
    return tf.numpy_function(f, [y_true, y_pred], tf.float32)
