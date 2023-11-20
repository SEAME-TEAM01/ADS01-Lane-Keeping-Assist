# train.py
import os
import numpy as np
import tensorflow as tf
from focal_loss import BinaryFocalLoss
from tensorflow.keras.callbacks import TerminateOnNaN, ModelCheckpoint, EarlyStopping, TensorBoard
import datetime
from model import unet_model
from dataset import LaneDataset
from utils import iou, split_dataset
from loss import instance_loss

BASE_DIR = '.'

LR = 1e-4 # Learning Rate
EPOCHS = 100
BS = 24 # Batch Size
LossWeights = [10, 1] # Loss function weights for Binary Segmentation and Instance Segmentation

terminate = TerminateOnNaN()
date_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
earlyStop = EarlyStopping(monitor='val_loss', patience=4)
filepath = BASE_DIR +  '/log/' + date_time
checkpoint = ModelCheckpoint(filepath=os.path.join(filepath, 'lanenet_ckpt.epoch{epoch:02d}-loss{loss:.2f}.h5'),
                            monitor='val_loss',
                            verbose=1,
                            save_best_only=True,
                            )

Lane = LaneDataset(write=False)
model = unet_model(256, 512, 3)
X_train, X_val, bin_train, bin_val, ins_train, ins_val = split_dataset(Lane)


history = model.fit(X_train, bin_train,
                    batch_size=BS,
                    verbose=1,
                    epochs=EPOCHS,
                    validation_data=(X_val, bin_val),
                    shuffle=False,
                    callbacks=[terminate, checkpoint, earlyStop])

np.save(os.path.join(BASE_DIR, 'log', date_time, 'lane4_lena_6_model.npy'), history.history)
model.save(os.path.join(BASE_DIR, 'log', date_time,'unet-epoch{epoch:02d}-{date_time}-final.h5'))
