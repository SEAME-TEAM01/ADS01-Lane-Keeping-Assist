# dataset.py
import os
import json
import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from multiprocessing import Pool
import multiprocessing

DATASET_DIR = 'dataset/TUSimple/train_set/'

def process_line(args):
  line, dataset_path, write, resize= args
  info = json.loads(line)
  img_path = os.path.join(dataset_path, info['raw_file'])
  lanes = info['lanes']
  h_samples = info['h_samples']

  raw_img = cv2.imread(img_path)
  raw_img = Image.fromarray(raw_img)
  raw_img = raw_img.resize(resize)
  original_img = np.array(raw_img, dtype=np.uint8)

  if (write == True):
    bin_mask = np.zeros_like(raw_img).astype(np.uint8)
    ins_mask = np.zeros_like(raw_img).astype(np.uint8)

    lanes = [[(x,y) for (x,y) in zip(lane, h_samples) if x >=0] for lane in lanes]

    color_ins = [[70,70,70],[120,120,120],[20,20,20],[170,170,170]]
    color_bin = [[255,255,255],[255,255,255],[255,255,255],[255,255,255]]

    for i in range(len(lanes)):
      if (len(lanes[i]) == 0):
        continue
      else:
        cv2.polylines(ins_mask, np.int32([lanes[i]]), isClosed=False, color=color_ins[i], thickness=5)
        cv2.polylines(bin_mask, np.int32([lanes[i]]), isClosed=False, color=color_bin[i], thickness=5)

    cv2.imwrite(img_path.split('.jpg')[0]+ '_bin.jpg', bin_mask)
    cv2.imwrite(img_path.split('.jpg')[0]+ '_ins.jpg', ins_mask)
  else:
    bin_mask = cv2.imread(img_path.split('.jpg')[0] + '_bin.jpg')
    ins_mask = cv2.imread(img_path.split('.jpg')[0]+ '_ins.jpg')

  bin_mask = Image.fromarray(bin_mask)
  bin_mask = bin_mask.resize(resize)
  label_bin = np.zeros([resize[1], resize[0]], dtype=np.uint8)
  label_bin = np.array(bin_mask, dtype=np.uint8)
  label_bin[label_bin != 0] = 1

  ins_mask = Image.fromarray(ins_mask)
  ins_mask = ins_mask.resize(resize)
  ins_mask = np.array(ins_mask, dtype=np.uint8)
  return original_img, label_bin, ins_mask


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
          for suffix in ('0313','0531',)
      ]
    elif self.mode == 'eval':
      label_files = [
          os.path.join(self.dataset_path, f"label_data_{suffix}.json")
          for suffix in ('0601',)
      ]

    for label_file in label_files:
      self.process_label_file(label_file, write=False, resize=(512, 256))
    self.data = np.array(self.data)
    self.bin_label = np.array(self.bin_label)
    self.ins_label = np.array(self.ins_label)

  def process_label_file(self, file_path, write, resize):
    with open(file_path) as f:
        lines = f.readlines()

    num_workers = multiprocessing.cpu_count()
    pool = Pool(processes=num_workers)

    args = ((line, self.dataset_path, write, resize) for line in lines)

    for result in tqdm(pool.imap(process_line, args, chunksize=1),
                       total=len(lines),
                       desc="Processing lines"):
        processed_data, label_bin, ins_mask = result
        self.data.append(processed_data)
        self.bin_label.append(label_bin)
        self.ins_label.append(ins_mask)

    pool.close()
    pool.join()
