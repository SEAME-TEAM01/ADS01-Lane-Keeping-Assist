# ------------------------------------------------------------------------------
# Library Import
import  cv2
import  numpy as np
import  tensorflow as tf

from    tensorflow.keras.models \
        import  load_model
from    piracer.vehicles \
        import  PiRacerStandard

# Custom Library Import
from    srcs.colors \
        import  *
from    srcs.variables \
        import  *
from    srcs.preprocess \
        import  preprocessing, \
                detect_orange_lines

# ------------------------------------------------------------------------------
# Run
def run():
    capture = cv2.VideoCapture(VIDEO)
    vehicle = PiRacerStandard()
    model   = load_model(MODEL, compile=False)
    capture.set(cv2.CAP_PROP_FPS, FPS)

    try:
        vehicle.set_steering_percent(STEERING_INIT)
        vehicle.set_throttle_percent(THROTTLE_INIT)

        frame_cnt = 0
        excep_cnt = 0
        while capture.isOpened():
            rst, frame = capture.read()
            if not rst:
                print(
                    f"{RED}{BOL}[FAILURE]{RES}    ",
                    f"Failed to grab frame. Check the camera[{BOL}/dev/video0{RES}]",
                )
                break
            if (len(detect_orange_lines(frame)) < 2):
                excep_cnt += 1
            else:
                excep_cnt = 0
            if (excep_cnt > 15):
                vehicle.set_steering_percent(STEERING_INIT * STEERING_PARAM)
                vehicle.set_throttle_percent(-1 * THROTTLE * THROTTLE_PARAM)
            elif (excep_cnt > 30):
                print(
                    f"{RED}{BOL}[FAILURE]{RES}    ",
                    f"Car could not find right way. Please let me back in track 😒",
                )
                break
            if (frame_cnt % 4 == 0):
                frame = preprocessing(frame, mode=1)
                frame = frame.reshape(1, frame.shape[0], frame.shape[1], 3)
                throttle = THROTTLE
                steering = STEERING_INIT

                predict = model.predict(frame)
                predict_label = np.argmax(predict, axis=1)[0]
                print(predict, predict_label)
                if predict_label == 0:
                    steering = STEERING_INIT
                elif predict_label == 1:
                    steering = STEERING_LEFT
                elif predict_label == 2:
                    steering = STEERING_RIGHT
                vehicle.set_throttle_percent(throttle * THROTTLE_PARAM)
                vehicle.set_steering_percent(steering * STEERING_PARAM)
            frame_cnt += 1


    except Exception as exception:
        print(
            f"{RED}{BOL}[FAILURE]{RES}    ",
            f"Unexpected exception has occured.\n",
            '-'*TERM_SIZE, "\n",
            exception, "\n",
            '-'*TERM_SIZE,
        )

    finally:
        vehicle.set_steering_percent(THROTTLE_INIT)
        vehicle.set_throttle_percent(STEERING_INIT)

# ------------------------------------------------------------------------------
# Main
if  __name__ == "__main__":
    run()