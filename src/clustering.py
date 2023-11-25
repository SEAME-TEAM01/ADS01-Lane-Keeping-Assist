import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import hdbscan
from loss import dice_coef, dice_loss
import tensorflow.keras as keras
from dataset import LaneDataset
from dotenv import load_dotenv
# from predict import test_predict
load_dotenv('.env')

def HDBSCAN_cluster(lanes):
  """
  Clusters a list of lane coordinates using HDBSCAN.

  params lanes: List of (x, y) tuples representing lane coordinates.
  """

  lanes_df = lanes_to_dataframe(lanes)

  cluster = hdbscan.HDBSCAN(min_cluster_size=10)
  cluster_labels = cluster.fit_predict(lanes_df)
  lanes_df['cluster'] = cluster_labels
  return lanes_df


def lanes_to_dataframe(lanes):
    """
    Converts a list of lane coordinates to a Pandas DataFrame.

    param lanes: List of (x, y) tuples representing lane coordinates.
    """
    df = pd.DataFrame(lanes, columns=['x', 'y'])
    df = df.sort_values(by='y', ascending=False)
    df = df.reset_index(drop=True)
    return df

def test():
  Lane = LaneDataset(train=False)
  SAMPLE_IMAGES = Lane.X_train
  model = keras.models.load_model(os.getenv('MODEL_PATH'), custom_objects={'dice_coef': dice_coef, 'dice_loss': dice_loss})
  # lanes = test_predict(SAMPLE_IMAGES, model)
  lanes =[]
  for lane in lanes:
    df = HDBSCAN_cluster(lane)
    print(df.head(n=50))
    plt.scatter(df['x'], df['y'], c=df['cluster'], cmap='rainbow')
    plt.show()
