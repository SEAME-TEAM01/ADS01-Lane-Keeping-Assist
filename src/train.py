# train.py
import os
import numpy as np
import tensorflow as tf
from focal_loss import BinaryFocalLoss
from tensorflow.keras.callbacks import TerminateOnNaN, ModelCheckpoint, EarlyStopping, TensorBoard
import datetime
from model import unet_model
from dataset import LaneDataset

SAVE_PATH = 'YOUR_SAVE_PATH'
EPOCHS = 50

Lane = LaneDataset(write=False)
model = unet_model(256, 512, 3)

terminate = TerminateOnNaN()
date_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
earlyStop = EarlyStopping(monitor='val_loss', patience=4)
filepath = SAVE_PATH +  '/output/' + date_time
checkpoint = ModelCheckpoint(filepath=os.path.join(filepath, 'unet-checkpoint.h5'),
                            monitor='val_loss',
                            verbose=1,
                            save_best_only=True,
                            )


history = model.fit(Lane.batched_train_dataset,
                    verbose=1,
                    epochs=EPOCHS,
                    validation_data=Lane.batched_val_dataset,
                    shuffle=True,
                    callbacks=[terminate, checkpoint, earlyStop])
