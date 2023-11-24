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

Lane = LaneDataset(train=True)
SAMPLE_IMAGES = Lane.X_train
model = keras.models.load_model(os.getenv('MODEL_PATH'), custom_objects={'dice_coef': dice_coef, 'dice_loss': dice_loss})

def lanes_to_dataframe(lanes):
    """
    Converts a list of lane coordinates to a Pandas DataFrame.
    """
    df = pd.DataFrame(lanes, columns=['x', 'y'])
    df = df.sort_values(by='y', ascending=False)
    df = df.reset_index(drop=True)
    return df

lanes = test_predict(SAMPLE_IMAGES, model)
lanes_df = lanes_to_dataframe(lanes)
plt.scatter(lanes_df['x'], lanes_df['y'])
plt.show()

scaler = MinMaxScaler()
scaler.fit(lanes_df[['x']])
lanes_df['x'] = scaler.transform(lanes_df[['x']])
scaler.fit(lanes_df[['y']])
lanes_df['y'] = scaler.transform(lanes_df[['y']])
print(lanes_df)

clusterer = hdbscan.HDBSCAN(min_cluster_size=10)
cluster_labels = clusterer.fit_predict(lanes_df)
lanes_df['cluster'] = cluster_labels
print(lanes_df)
plt.scatter(lanes_df['x'], lanes_df['y'], c=lanes_df['cluster'])
plt.show()
