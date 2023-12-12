from        piracer.vehicles    import  PiRacerStandard
from        piracer.gamepads    import  ShanWanGamepad
import      cv2                 as      cv2
import      time                as      tim
import      traceback           as      trc
import      multiprocessing     as      mlp
import      os

CSVFILE     = "dataset/record/record.csv"

def process_control_car():
    print("car control started.")
    pad = ShanWanGamepad()
    veh = PiRacerStandard()

    try:
        while True:
            gamepad_input   = pad.read_data()
            throttle        = gamepad_input.analog_stick_left.y
            steering        = gamepad_input.analog_stick_right.x

            veh.set_steering_percent(steering * 1.3)
            veh.set_throttle_percent(throttle * 0.6)

            # Log steering and frame info
            with open(CSVFILE, "a") as csv_file:
                csv_file.write(f"{tim.time()},{steering}{throttle}\n")

    except Exception as e:
        print("An error occurred:", e)
        trc.print_exc()
        veh.set_steering_percent(0)
        veh.set_throttle_percent(0)

    except KeyboardInterrupt:
        print("Car control process has been stopped.")
        veh.set_steering_percent(0)
        veh.set_throttle_percent(0)

def process_capture_img():
    print("log data started.")
    # Start video capture
    cap = cv2.VideoCapture(0)
    
    # Verify that the camera is available
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    try:
        while True:
            rst, frame = cap.read()
            frame = cv2.flip(frame, 0)

            # Check if frame captured successfully
            if not rst:
                print("Error: Could not read frame.")
                break
            
            cv2.imwrite(f'dataset/record/frames/frame_{tim.time()}.jpg', frame)
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    if not os.path.exists(CSVFILE):
        with open(CSVFILE, "w") as file:
            file.write("miliseconds,steering,throttle\n")

    pr1 = mlp.Process(
        name="python3-car-control",
        target=process_control_car,
    )
    pr2 = mlp.Process(
        name="python3-capture-img",
        target=process_capture_img,
    )
    pr1.start()
    pr2.start()
    pr1.join()
    pr2.join()
