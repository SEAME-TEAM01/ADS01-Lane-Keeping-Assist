# - import python library
import os
import cv2
import time

# - import color variables
from util.color import *

# - variables
VIDEO = 0
DATASET = "dataset/"
CSV = DATASET+"record.csv"
TERM_SIZE = os.get_terminal_size().columns

# - capture img program
def record_data(vehicle):
    # Infor program start
    print(
        f"{CYA}{BOL}[INFORMT]{RES}    ",
        f"Capture-img process has been started at:",
        "\n",
        f"{CYA}{BOL}         {RES}    ",
        f"{time.time()}"
    )

    # file check
    index = 0
    if  not os.path.exists(CSV):
        with open(CSV, "w") as file:
            file.write("index,steering,throttle_left,throttle_right,direction(front-0/left-1/right-2)\n")
    else:
        with open(CSV, "r") as file:
            lines = file.readlines()
            if len(lines) > 1:
                last_line = lines[-1].strip()
                last_index = int(last_line.split(",")[0])
                index = last_index + 1



    # Start video capture
    cap = cv2.VideoCapture(VIDEO)
    
    # Verify that the camera is available
    if not cap.isOpened():
        print(
            f"{RED}{BOL}[FAILURE]{RES}    ",
            f"Can't open camera. Please check the connection!"
        )
        return
    
    try:
        while True:
            rst, frame  = cap.read()
            frame       = cv2.flip(frame, -1)
            steering    = vehicle.get_steering_raw_data()
            throttle    = vehicle.get_throttle_raw_data()
            direction   = 0
            if (steering < 4000):
                direction = 1
            elif (steering > 5000):
                direction = 2
            # elif (steering == 4560):
            #     print(
            #         f"{GRE}{BOL}[SUCCESS]{RES}    ",
            #         f"Steering is exactly 4560!")

            if not rst:
                print(
                    f"{RED}{BOL}[FAILURE]{RES}    ",
                    f"Can't read the frame.",
                    "\n",
                    f"{RED}{BOL}         {RES}    ",
                    f"Please follow steps to solve the problem.",
                    "\n",
                    f"{RED}{BOL}         {RES}    ",
                    f" - Check camera connection and drivers.",
                    "\n",
                    f"{RED}{BOL}         {RES}    ",
                    f" - Check is another application using camera."
                )
                break
            
            cv2.imwrite(f'{DATASET}/frames/frame_{index}_{steering}.jpg', frame)
            with open(CSV, "a") as csv_file:
                csv_file.write(f"{index},{steering},{throttle[0]},{throttle[1]},{direction}\n")
            index += 1

    except Exception as exception:
        print(
            f"{RED}{BOL}[FAILURE]{RES}    ",
            f"Unexpected exception has occured.\n",
            '-'*TERM_SIZE, "\n",
            exception, "\n",
            '-'*TERM_SIZE,
        )
    finally:
        cap.release()
        cv2.destroyAllWindows()
