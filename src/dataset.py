import os
import json
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool
import multiprocessing
from sklearn.model_selection import train_test_split
import tensorflow as tf
from dotenv import load_dotenv

load_dotenv('.env')

class LaneDataset():
  def __init__(self, dataset_path=os.path.join(os.getcwd(),os.getenv('DATASET_PATH')), train=True, write=False, size=(512,256)):
    self.dataset_path = dataset_path
    self.mode = 'train' if train else 'eval'
    self.write = write
    self.image_size = size
    self.X_train = []
    self.y_train = []
    self.BATCH_SIZE = 32
    self.batched_train_dataset = None
    self.batched_val_dataset = None

    if self.mode == 'train':
      label_files = [
          os.path.join(self.dataset_path, f"label_data_{suffix}.json")
          for suffix in ('0313','0531',)
      ]
    elif self.mode == 'eval':
      label_files = [
          os.path.join(self.dataset_path, f"label_data_{suffix}.json")
          for suffix in ('0601',)
      ]

    for label_file in label_files:
      self.process_label_file(label_file)

    X_train, X_val, y_train, y_val = train_test_split(self.X_train, self.y_train, test_size=0.2, random_state=42)

    X_train = tf.data.Dataset.from_tensor_slices(X_train)
    y_train = tf.data.Dataset.from_tensor_slices(y_train)

    X_val = tf.data.Dataset.from_tensor_slices(X_val)
    y_val = tf.data.Dataset.from_tensor_slices(y_val)

    self.X_train = X_train.map(self.preprocess_image)
    self.y_train = y_train.map(self.preprocess_target)

    self.X_val = X_val.map(self.preprocess_image)
    self.y_val = y_val.map(self.preprocess_target)

    train_dataset = tf.data.Dataset.zip((self.X_train, self.y_train))
    val_dataset = tf.data.Dataset.zip((self.X_val, self.y_val))

    batched_train_dataset = train_dataset.batch(self.BATCH_SIZE)
    batched_val_dataset = val_dataset.batch(self.BATCH_SIZE)

    AUTOTUNE = tf.data.experimental.AUTOTUNE
    self.batched_train_dataset = batched_train_dataset.prefetch(buffer_size=AUTOTUNE)
    self.batched_val_dataset = batched_val_dataset.prefetch(buffer_size=AUTOTUNE)


  def process_label_file(self, file_path):
    with open(file_path) as f:
        lines = f.readlines()
    for line in tqdm(lines, desc="Processing lines"):
      info = json.loads(line)
      raw_path = os.path.join(self.dataset_path, info['raw_file'])
      bin_path = raw_path.split('.jpg')[0] + '_bin.jpg'
      self.X_train.append(raw_path)
      self.y_train.append(bin_path)

    # num_workers = multiprocessing.cpu_count()
    # with Pool(processes=num_workers) as pool:
    #   results = list(tqdm(pool.starmap(self.process_line, [(line, self.dataset_path) for line in lines]), total=len(lines), desc="Processing lines"))

    #   for raw_path, bin_path in results:
    #       self.X_train.append(raw_path)
    #       self.y_train.append(bin_path)


  def process_line(self, line, dataset_path):
    info = json.loads(line)
    raw_path = os.path.join(dataset_path, info['raw_file'])
    bin_path = raw_path.split('.jpg')[0] + '_bin.jpg'
    return raw_path, bin_path

  def preprocess_image(self, file_path):
    img = tf.io.read_file(file_path)
    img = tf.image.decode_jpeg(img, channels=3) # Returned as uint8
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = tf.image.resize(img, [256, 512], method = 'nearest')
    return img

  def preprocess_target(self, file_path):
    mask = tf.io.read_file(file_path)
    mask = tf.image.decode_image(mask, expand_animations=False, dtype=tf.float32)
    mask = tf.math.reduce_max(mask, axis=-1, keepdims=True)
    mask = tf.image.resize(mask, [256, 512], method = 'nearest')
    return mask
