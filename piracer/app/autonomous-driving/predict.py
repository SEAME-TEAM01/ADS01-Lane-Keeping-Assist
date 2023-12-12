# ------------------------------------------------------------------------------
# Library Import
import  os
import  cv2
import  numpy as np
import  pandas as pd
import  matplotlib.pyplot as plt

import  tensorflow as tf
from    tensorflow.keras.models \
        import  load_model
from    tensorflow.keras.utils \
        import  to_categorical

# Custom Library Import
from    srcs.colors \
        import  *
from    srcs.variables \
        import  *
from    srcs.preprocess \
        import  load_image
from    srcs.plot \
        import  plot_predict

# ------------------------------------------------------------------------------
# predict
def predict_test(data_pred, model):
    predictions = model.predict(data_pred)
    max_indices = np.argmax(predictions, axis=1)
    num_classes = predictions.shape[1]
    one_hot_encoded = np.zeros((predictions.shape[0], num_classes))
    one_hot_encoded[np.arange(predictions.shape[0]), max_indices] = 1

    return one_hot_encoded

def predict():
    csv_org         = pd.read_csv(CSV)
    csv_predict     = pd.read_csv(CSV_PRED)
    label_list      = ["Front", "Left", "Right"]
    label_dict      = {0: label_list[0], 1: label_list[1], 2: label_list[2]}
    model           = load_model(MODEL)

    prd_indexes     = csv_predict['index'].values
    rows            = csv_org[csv_org['index'].isin(prd_indexes)]
    images, labels  = load_image(rows)

    labels_predict  = predict_test(images, model)
    labels_predict  = np.argmax(labels_predict, axis=1)  # Convert from one-hot to label format
    labels_actual   = np.argmax(labels, axis=1)          # Convert from one-hot to label format

    accuracy        = np.mean(labels_predict == labels_actual)
    print(
        f"{CYA}{BOL}[INFORMT]{RES}    ",
        f"Prediction accuracy: {GRE}{BOL}{accuracy * 100:.2f}{RES}%",
    )
    
    labels_actual   = [label_dict[idx] for idx in labels_actual]
    labels_predict  = [label_dict[idx] for idx in labels_predict]

    plot_predict(labels_actual, labels_predict, label_list)

# ------------------------------------------------------------------------------
# Main
if  __name__ == "__main__":
    predict()