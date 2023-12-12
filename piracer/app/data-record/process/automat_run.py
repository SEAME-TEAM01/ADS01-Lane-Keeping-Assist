# - import python library
import os
import time
import traceback

# - import color variables
from util.color import *

# - variables
CSVFILE = "dataset/record.csv"
TERM_SIZE = os.get_terminal_size().columns
THROTTLE_PARAM = 1.0
THROTTLE_INIT = 0.0
STEERING_PARAM = -1.5
STEERING_INIT = 0

# - automat run program
def run_action(vehicle, throttle, steering, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        vehicle.set_throttle_percent(throttle * THROTTLE_PARAM)
        vehicle.set_steering_percent(steering * STEERING_PARAM)
    vehicle.set_steering_percent(STEERING_INIT)

def automat_run_left(vehicle):
    # Infor program start
    print(
        f"{CYA}{BOL}[INFORMT]{RES}    ",
        f"Automat-run process has been started at:",
        "\n",
        f"{CYA}{BOL}         {RES}    ",
        f"{time.time()}"
    )

    # Initialize objects
    vehicle.set_throttle_percent(THROTTLE_INIT)
    vehicle.set_steering_percent(STEERING_INIT)

    try:
        run_action(
            vehicle,
            throttle=0.3,
            steering=STEERING_INIT,
            duration=2.5
        )
        while True:
            run_action(
                vehicle,
                throttle=0.3,
                steering=-0.57,
                duration=4.2
            )
            run_action(
                vehicle,
                throttle=0.3,
                steering=STEERING_INIT,
                duration=2
            )
            
    except Exception as exception:
        print(
            f"{RED}{BOL}[FAILURE]{RES}    ",
            f"Unexpected exception has occured.\n",
            f"{BOL}", "-"*TERM_SIZE, f"{RES}\n",
            exception,
            "-" * TERM_SIZE,
        )
        print(
            f"{RED}{BOL}[FAILURE]{RES}    ",
            f"Exception log by traceback:\n",
            f"{BOL}", "-" * TERM_SIZE)
        traceback.print_exc()
        print(
            "-" * TERM_SIZE, f"{RES}",
        )
    finally:
        vehicle.set_steering_percent(THROTTLE_INIT)
        vehicle.set_throttle_percent(STEERING_INIT)

def automat_run_right(vehicle):
    # Infor program start
    print(
        f"{CYA}{BOL}[INFORMT]{RES}    ",
        f"Automat-run process has been started at:",
        "\n",
        f"{CYA}{BOL}         {RES}    ",
        f"{time.time()}"
    )

    # Initialize objects
    vehicle.set_throttle_percent(THROTTLE_INIT)
    vehicle.set_steering_percent(STEERING_INIT)

    try:
        run_action(
            vehicle,
            throttle=0.3,
            steering=STEERING_INIT,
            duration=2.5
        )
        while True:
            run_action(
                vehicle,
                throttle=0.3,
                steering=0.76,
                duration=4.7
            )
            run_action(
                vehicle,
                throttle=0.3,
                steering=STEERING_INIT,
                duration=1.8
            )

    except Exception as exception:
        print(
            f"{RED}{BOL}[FAILURE]{RES}    ",
            f"Unexpected exception has occured.\n",
            f"{BOL}", "-"*TERM_SIZE, f"{RES}\n",
            exception,
            "-" * TERM_SIZE,
        )
        print(
            f"{RED}{BOL}[FAILURE]{RES}    ",
            f"Exception log by traceback:\n",
            f"{BOL}", "-" * TERM_SIZE)
        traceback.print_exc()
        print(
            "-" * TERM_SIZE, f"{RES}",
        )
    finally:
        vehicle.set_steering_percent(THROTTLE_INIT)
        vehicle.set_throttle_percent(STEERING_INIT)