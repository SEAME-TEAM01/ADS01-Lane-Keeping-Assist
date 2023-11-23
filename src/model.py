# model.py
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Input, Rescaling, Conv2D, MaxPooling2D, UpSampling2D, concatenate, Conv2DTranspose, BatchNormalization, Dropout
from loss import dice_coef, dice_loss

def encoder(inputs, outchan):
  x = Conv2D(outchan, (3,3), activation='relu', padding='same', kernel_initializer='he_normal')(inputs)
  x = Conv2D(outchan, (3,3), activation='relu', padding='same', kernel_initializer='he_normal')(x)

  p = MaxPooling2D((2,2), strides=2)(x)
  return x, p

def decoder(inputs, skip_features, outchan):
  x = Conv2DTranspose(outchan, (2,2), strides=2, padding='same')(inputs)

  x = concatenate([x, skip_features])
  x = Conv2D(outchan, (3,3), activation='relu', padding='same', kernel_initializer='he_normal')(x)
  x = Conv2D(outchan, (3,3), activation='relu', padding='same', kernel_initializer='he_normal')(x)
  return x

def bottleneck(inputs, outchan):
  x = Conv2D(outchan, (3,3), activation='relu', padding='same', kernel_initializer='he_normal')(inputs)
  x = Conv2D(outchan, (3,3), activation='relu', padding='same', kernel_initializer='he_normal')(x)
  x = Dropout(0.4)(x)
  return x

def unet_model(HEIGHT, WIDTH, CHANNELS):
  input_tensor = Input((HEIGHT, WIDTH, CHANNELS))
  s = tf.keras.layers.Lambda(lambda x: x/255)(input_tensor)

  # Contracting Path
  c1,p1 = encoder(s, 64)
  c2,p2 = encoder(p1, 128)
  c3,p3 = encoder(p2, 256)
  c4,p4 = encoder(p3, 512)

  # Bottleneck
  b1 = bottleneck(p4, 1024)

  # Expansive Path bin
  c6_bin = decoder(b1, c4, 512)
  c7_bin = decoder(c6_bin, c3, 256)
  c8_bin = decoder(c7_bin, c2, 128)
  c9_bin = decoder(c8_bin, c1, 64)

  bin_seg = Conv2D(1, (1,1), activation='sigmoid', name='bin_seg')(c9_bin)

  model = Model(inputs=[input_tensor], outputs=[bin_seg])

  model.compile(optimizer=Adam(learning_rate=1e-4), loss=[dice_loss], metrics=[dice_coef])
  return model
