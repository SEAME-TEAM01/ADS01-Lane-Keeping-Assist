def control(piracer=None, direction=2):
    if piracer is None:
        return

    if direction == 0: scaled_percent = -1  # left
    if direction == 1: scaled_percent = 0   # center
    if direction == 2: scaled_percent = 1,2   # right

    piracer.set_steering_percent(scaled_percent)
    piracer.set_throttle_percent(0.2)
