from PIL import Image
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from dataset import LaneDataset

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

def turn_on_gpu():
  gpus = tf.config.experimental.list_physical_devices('GPU')
  if gpus:
      try:
          # Currently, memory growth needs to be the same across GPUs
          for gpu in gpus:
              tf.config.experimental.set_memory_growth(gpu, True)
          logical_gpus = tf.config.experimental.list_logical_devices('GPU')
          print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
      except RuntimeError as e:
          # Memory growth must be set before GPUs have been initialized
          print(e)

def visualize_history(history_path):
  # Load the history from the .npy file
  history = np.load(history_path, allow_pickle=True).item()

  # Plotting each metric in the history
  fig, axes = plt.subplots(3, 2, figsize=(15, 15))  # Adjust the size as needed

  # Plot training and validation loss
  axes[0, 0].plot(history['loss'], label='Training Loss')
  axes[0, 0].plot(history['val_loss'], label='Validation Loss')
  axes[0, 0].set_title('Training and Validation Loss')
  axes[0, 0].set_xlabel('Epochs')
  axes[0, 0].set_ylabel('Loss')
  axes[0, 0].legend()

  # Plot binary segmentation loss
  axes[0, 1].plot(history['bin_seg_loss'], label='Binary Segmentation Loss')
  axes[0, 1].plot(history['val_bin_seg_loss'], label='Validation Binary Segmentation Loss')
  axes[0, 1].set_title('Training and Validation Binary Segmentation Loss')
  axes[0, 1].set_xlabel('Epochs')
  axes[0, 1].set_ylabel('Loss')
  axes[0, 1].legend()

  # Plot instance segmentation loss
  axes[1, 0].plot(history['ins_seg_loss'], label='Instance Segmentation Loss')
  axes[1, 0].plot(history['val_ins_seg_loss'], label='Validation Instance Segmentation Loss')
  axes[1, 0].set_title('Training and Validation Instance Segmentation Loss')
  axes[1, 0].set_xlabel('Epochs')
  axes[1, 0].set_ylabel('Loss')
  axes[1, 0].legend()

  # Plot binary segmentation IoU
  axes[1, 1].plot(history['bin_seg_iou'], label='Binary Segmentation IoU')
  axes[1, 1].plot(history['val_bin_seg_iou'], label='Validation Binary Segmentation IoU')
  axes[1, 1].set_title('Training and Validation Binary Segmentation IoU')
  axes[1, 1].set_xlabel('Epochs')
  axes[1, 1].set_ylabel('IoU')
  axes[1, 1].legend()

  # Plot instance segmentation accuracy
  axes[2, 0].plot(history['ins_seg_accuracy'], label='Instance Segmentation Accuracy')
  axes[2, 0].plot(history['val_ins_seg_accuracy'], label='Validation Instance Segmentation Accuracy')
  axes[2, 0].set_title('Training and Validation Instance Segmentation Accuracy')
  axes[2, 0].set_xlabel('Epochs')
  axes[2, 0].set_ylabel('Accuracy')
  axes[2, 0].legend()

  # Adjust layout and display the plots
  plt.tight_layout()
  plt.show()
