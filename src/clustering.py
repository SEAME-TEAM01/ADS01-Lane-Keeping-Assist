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
from predict import test_predict
load_dotenv('.env')

def HDBSCAN_cluster(lanes):
  """
  Clusters a list of lane coordinates using HDBSCAN.

  params lanes: List of (x, y) tuples representing lane coordinates.
  """

  lanes_df = lanes_to_dataframe(lanes)

  scaler = MinMaxScaler()
  scaler.fit(lanes_df[['x']])
  lanes_df['x'] = scaler.transform(lanes_df[['x']])
  scaler.fit(lanes_df[['y']])
  lanes_df['y'] = scaler.transform(lanes_df[['y']])

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
