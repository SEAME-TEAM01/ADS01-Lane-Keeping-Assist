# - import python library
import os
import sys
from multiprocessing import Process

from piracer.vehicles import PiRacerStandard
from piracer.gamepads import ShanWanGamepad

# - import multiprocess functions
from process import record_data, control_car, automat_run

# - import color variables
from util.color import *

TERM_SIZE = os.get_terminal_size().columns - 2
STEERING_INIT = -0.2
THROTTLE_INIT = 0.0

def check_cwd():
    """
    Check is current working directory [~/.../app/data-record/]
    """

    folder = "app/data-record"
    cur = os.getcwd()

    if  not cur.endswith(folder):
        print(
            f"{RED}{BOL}[FAILURE]{RES}    ",
            f"You are working on {YEL}wrong directory.{RES}",
            "\n",
            f"{RED}{BOL}         {RES}    ",
            f"Please launch program in [.../{folder}]."
        )
        sys.exit(1)

def multiprocess_create(*args):
    prcs = []
    for arg in args:
        prc = Process(
            name    = arg[0],
            target  = arg[1],
            args    = arg[2],
        )
        prcs.append(prc)
    return prcs


# - main
if  __name__ == "__main__":
    check_cwd()

    prcs = []
    try:
        vehicle = PiRacerStandard()
        gamepad = ShanWanGamepad()
        vehicle.set_steering_percent(STEERING_INIT)
        vehicle.set_throttle_percent(THROTTLE_INIT)

        prcs = multiprocess_create(
            ["python3-automat-run", automat_run.automat_run_left,  (vehicle, )],
            # ["python3-automat-run", automat_run.automat_run_right, (vehicle, )],
            # ["python3-control-car", control_car.control_car, (vehicle, gamepad)],
            ["python3-record-data", record_data.record_data, (vehicle, )],
        )
        for prc in prcs:
            prc.start()
        for prc in prcs:
            prc.join()
    except KeyboardInterrupt:
        print(
            f"\n{CYA}{BOL}[INFORMT]{RES}    ",
            f"Program has been stoped by Keyboard Inturrupt.",
            "\n",
            f"{CYA}{BOL}         {RES}    ",
            f"{GRE}{BOL}GOOD BYE!{RES}"
        )
    except Exception as exception:
        print(
            f"{RED}{BOL}[FAILURE]{RES}    ",
            f"Unexpected exception has occured.\n",
            '-'*TERM_SIZE, "\n",
            exception, "\n",
            '-'*TERM_SIZE,
        )
    finally:
        for prc in prcs:
            prc.terminate()
        vehicle.set_steering_percent(STEERING_INIT)
        vehicle.set_throttle_percent(THROTTLE_INIT)
