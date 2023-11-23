import tensorflow as tf
import matplotlib.pyplot as plt
import tensorflow.keras as keras
from loss import dice_coef, dice_loss
from dataset import LaneDataset

MODEL_PATH = 'YOUR_MODEL_PATH'

def display(display_list):
    plt.figure(figsize=(15, 15))

    title = ['Input Image', 'Predicted Mask']

    for i in range(len(display_list)):
        plt.subplot(1, len(display_list), i+1)
        plt.title(title[i])
        plt.imshow(tf.keras.preprocessing.image.array_to_img(display_list[i]))
        plt.axis('off')
    plt.show()

def create_mask(pred_mask):
    mask = pred_mask[..., -1] >= 0.5
    pred_mask[..., -1] = tf.where(mask, 1, 0)
    return pred_mask[0]

def show_predictions(model, dataset=None, num=1):
    """
    Displays the first image of each of the num batches
    """
    if dataset:
        for image in dataset.take(num):
            pred_mask = model.predict(image)
            display([image[0], create_mask(pred_mask)])

Lane = LaneDataset(train=False)
custom_model = keras.models.load_model(MODEL_PATH, custom_objects={'dice_coef': dice_coef, 'dice_loss': dice_loss})
show_predictions(model = custom_model, dataset = Lane.batched_train_dataset, num = 6)
