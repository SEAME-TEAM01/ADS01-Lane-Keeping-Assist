# dataset.py
import os
import json
import cv2
import numpy as np
import matplotlib.pyplot as plt

DATASET_DIR = '/dataset/TUSimple/tain_set/'

class LaneDataset():
  def __init__(self, dataset_path=DATASET_DIR, train=True, size=(512,256)):
    self.dataset_path = dataset_path
    self.mode = 'train' if train else 'eval'
    self.image_size = size
    self.data = []
    self.bin_label = []
    self.ins_label = []

    if self.mode == 'train':
      label_files = [
          os.path.join(self.dataset_path, f"label_data_{suffix}.json")
          for suffix in ('0313', '0531')
      ]
    elif self.mode == 'eval':
      label_files = [
          os.path.join(self.dataset_path, f"label_data_{suffix}.json")
          for suffix in ('0601')
      ]

    for label_file in label_files:
      self.process_label_file(label_file, write=False)

  def process_label_file(self, file_path, write):
    with open(file_path) as f:
      for line in f:
        info = json.loads(line)
        img_path = os.path.join(self.dataset_path, info['raw_file'])
        lanes = info['lanes']
        h_samples = info['h_samples']

        raw_img = cv2.imread(img_path)
        self.data.append(raw_img)
        lanes = [[(x,y) for (x,y) in zip(lane, h_samples) if x >=0] for lane in lanes]

        bin_mask = np.zeros_like(raw_img).astype(np.uint8)
        ins_mask = np.zeros_like(raw_img).astype(np.uint8)
        skip = False

        color_ins = [[70,70,70],[120,120,120],[20,20,20],[170,170,170]]
        color_bin = [[255,255,255],[255,255,255],[255,255,255],[255,255,255]]

        for i in range(len(lanes)):
          if (len(lanes[i]) == 0):
            skip = False
            break
          else:
            cv2.polylines(ins_mask, np.int32([lanes[i]]), isClosed=False, color=color_ins[i], thickness=5)
            cv2.polylines(bin_mask, np.int32([lanes[i]]), isClosed=False, color=color_bin[i], thickness=5)
            skip = False
        if skip == True:
          print('Number of lanes is not 4!')
        else:
          if (write == True):
            cv2.imwrite(img_path.split('.jpg')[0]+ '_bin.jpg', bin_mask)
            cv2.imwrite(img_path.split('.jpg')[0]+ '_ins.jpg', ins_mask)
          else:
            self.bin_label.append(bin_mask)
            self.ins_label.append(ins_mask)
