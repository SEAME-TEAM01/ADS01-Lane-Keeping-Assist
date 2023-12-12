# ------------------------------------------------------------------------------
# Library Import
import  os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 

import  cv2
import  numpy as np
import  pandas as pd
import  tensorflow as tf

from    tensorflow.keras.models \
        import  Sequential, \
                load_model
from    tensorflow.keras.layers \
        import  Conv2D, \
                MaxPooling2D, \
                Flatten, \
                Dense, \
                Dropout
from    tensorflow.keras.optimizers \
        import  Adam
from    tensorflow.keras.callbacks \
        import  ReduceLROnPlateau, \
                EarlyStopping
from    sklearn.model_selection \
        import  train_test_split

# Custom Library import
from    srcs.colors \
        import  *
from    srcs.variables \
        import  *
from    srcs.preprocess \
        import  load_image
from    srcs.plot \
        import  plot_fit
# ------------------------------------------------------------------------------ import plot_fit

# Model
def ft_new_model():
    model = Sequential([
        Conv2D(24, (5,5), activation='relu', input_shape=(HEIGHT, WIDTH, 3)),
        MaxPooling2D((2,2)),
        Conv2D(36, (5,5), activation='relu'),
        MaxPooling2D((2,2)),
        Conv2D(48, (5,5), activation='relu'),
        MaxPooling2D((2,2)),
        Flatten(),
        Dense(100, activation='relu'),
        Dropout(0.5),
        Dense(50, activation='relu'),
        Dropout(0.5),
        Dense(3, activation='softmax')  # 3 Classes : Front/Left/Right
    ])
    model.compile(
        optimizer   = Adam(learning_rate=0.0001),
        loss        = 'categorical_crossentropy',
        metrics     = ['accuracy']
    )
    return model

def ft_load_model():
    model = load_model(MODEL)
    model.compile(
        optimizer   = Adam(learning_rate=0.0001),
        loss        = 'categorical_crossentropy',
        metrics     = ['accuracy']
    )
    return model

# Callbacks
def ft_callbacks():
    lrscheduler = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=2,
        verbose=1
    )
    earlystop = EarlyStopping(
        monitor='val_loss',
        patience=5,
        verbose=1,
        restore_best_weights=True
    )
    callbacks = [lrscheduler, earlystop]

    return callbacks

# ------------------------------------------------------------------------------
# Fit
def fit():
    try:
        # Data load
        print(
            f"{CYA}{BOL}[INFORMT]{RES}    ",
            f"Dataset loading and Image loading:",
        )
        csv = pd.read_csv(CSV)
        data, label = load_image(csv)
        print(
            f"{CYA}{BOL}         {RES}    ",
            f"{GRE}{BOL}Completed.{RES}",
        )

        # Label distribution analysis
        print(
            f"{CYA}{BOL}[INFORMT]{RES}    ",
            f"Label distribution analysis:",
        )
        unique, counts = np.unique(np.argmax(label, axis=1), return_counts=True)
        label_dist = dict(zip(unique, counts))
        print(
            f"{CYA}{BOL}         {RES}    ",
            f"Label distribution in training data:\n",
            f"{CYA}{BOL}         {RES}    ",
            f"{BOL}{label_dist}{RES}\n",
            f"{CYA}{BOL}        {RES}    ",
            f"{GRE}{BOL}Completed.{RES}",
        )

        # Data shape
        print(
            f"{CYA}{BOL}[INFORMT]{RES}    ",
            f"Dataset reshaping and data split:",
        )
        data = data.reshape(data.shape[0], HEIGHT, WIDTH, 3)
        # - Splitting into Train (60%), tmp (40% -> will be split further into Validation and Predict)
        data_train, data_tmp, label_train, label_tmp, idx_train, idx_tmp = \
            train_test_split(
                data,
                label,
                csv['index'],  # Adding the index for tracking
                test_size=0.8,
                random_state=42,
                shuffle=True
            )
        # Splitting Temp into Validation (50% of 40% = 20%) and Predict (50% of 40% = 20%)
        data_test, data_pred, label_test, label_pred, idx_test, idx_pred = \
            train_test_split(
                data_tmp,
                label_tmp,
                idx_tmp,        # Using the temporary index for tracking
                test_size=0.5,
                random_state=42,
                shuffle=True
            )
        # Save indices of Predict set to a CSV
        pd.DataFrame({'index': idx_pred}).to_csv(CSV_PRED, index=False)
        print(
            f"{CYA}{BOL}         {RES}    ",
            f"{GRE}{BOL}Completed.{RES}",
            f"\n{CYA}{BOL}         {RES}    ",
            f"{GRE}{BOL}Indices of Predict set saved to {BOL}[{CSV_PRED}]{RES}.{RES}",
        )

        # CNN Model
        print(
            f"{CYA}{BOL}[INFORMT]{RES}    ",
            f"CNN Model Build:",
        )
        # model = ft_new_model()
        model = ft_load_model()
        print(
            f"{CYA}{BOL}         {RES}    ",
            f"{GRE}{BOL}Completed.{RES}",
        )

        # Scheduler & Callback setting
        print(
            f"{CYA}{BOL}[INFORMT]{RES}    ",
            f"Scheduler & Callback setting:",
        )
        callbacks = ft_callbacks()
        print(
            f"{CYA}{BOL}         {RES}    ",
            f"{GRE}{BOL}Completed.{RES}",
        )

        # Model Train
        print(
            f"{CYA}{BOL}[INFORMT]{RES}    ",
            f"Model train:\n",
            '-'*TERM_SIZE
        )
        history = model.fit(
            data_train,
            label_train,
            epochs = 10,
            validation_data = (data_test, label_test),
            batch_size = 32,
            verbose = 1,
            callbacks = callbacks
        )
        model.save(MODEL)
        print(
            f"{CYA}{BOL}         {RES}    ",
            f"{GRE}{BOL}Completed,{RES} model file is saved as \"{MODEL}\".",
        )

        plot_fit(history)

    except Exception as exception:
        print(
            f"{RED}{BOL}[FAILURE]{RES}    ",
            f"Unexpected exception has occured.\n",
            '-'*TERM_SIZE, "\n",
            f"{exception}\n",
            '-'*TERM_SIZE,
        )

# ------------------------------------------------------------------------------
# Main
if  __name__ == "__main__":
    fit()