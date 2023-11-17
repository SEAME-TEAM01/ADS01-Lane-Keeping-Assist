import os
import datetime
import tensorflow as tf
from focal_loss import BinaryFocalLoss
from tensorflow.keras.callbacks import TerminateOnNaN, ModelCheckpoint, EarlyStopping, TensorBoard
from loss import instance_loss
from utils import split_dataset, iou

BASE_DIR = './'

LR = 1e-4 # Learning Rate
EPOCHS = 100
BS = 15 # Batch Size
LossWeights = [10, 1] # Loss function weights for Binary Segmentation and Instance Segmentation

terminate = TerminateOnNaN()
earlyStop = EarlyStopping(monitor='var_loss', patience=4)
log_dir = BASE_DIR + '/log/fit/' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
filepath = BASE_DIR +  '/output/model/saved-model.hdf5'
ternsorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)
checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True,
                             save_wights_only=True, mode='auto', save_freq=1)

def train(model, Lane):
  X_train, X_test, bin_train, bin_test, ins_train, ins_test = split_dataset(Lane)
  tf.random.set_seed(40)
 # Define a learning rate schedule
  lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=LR,
    decay_steps=EPOCHS,
    decay_rate=0.96,
    staircase=True
  )
  optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)

  model.compile(optimizer=optimizer,
                loss=[BinaryFocalLoss(gamma=2), instance_loss],
                loss_weights=LossWeights,
                metrics={'bin_seg': iou, 'ins_seg': 'accuracy'}
                )

  history = model.fit(X_train, [bin_train, ins_train],
                      batch_size=BS,
                      verbose=1,
                      epochs=EPOCHS,
                      validation_data=(X_test, [bin_test, ins_test]),
                      shuffle=False,
                      callbacks=[terminate, ternsorboard_callback, checkpoint, earlyStop])

  np.save(os.path.join(BASE_DIR, '/output/history/lane4_lena_6_model.npy'), history.history)
  model.save(os.path.join(BASE_DIR, '/output/model/lane4_lena_6_model.hdf5'))
