#!/usr/bin/env python3
import time
from gpiozero import OutputDevice

# User Variables:
ON_THRESHOLD = 65  # (degrees Celsius) Fan kicks on at this temperature.
OFF_THRESHOLD = 55  # (degress Celsius) Fan shuts off at this temperature.
SLEEP_INTERVAL = 30  # (seconds) How often we check the core temperature.
GPIO_PIN = 17  # Which GPIO pin you're using to control the fan.
MIN_FAN_ON_TIME = 600  # (seconds) Minimum fan on time once it has been turned on.

def get_temp():
    """Get the core temperature.

    Read file from /sys to get CPU temp in temp in C *1000

    Returns:
        int: The core temperature in thousanths of degrees Celsius.
    """
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp_str = f.read()

    try:
        return int(temp_str) / 1000
    except (IndexError, ValueError,) as e:
        raise RuntimeError('Could not parse temperature output.') from e

if __name__ == '__main__':
    # Validate the on and off thresholds
    if OFF_THRESHOLD >= ON_THRESHOLD:
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')

    fan = OutputDevice(GPIO_PIN)
    fan_start_time = None

    while True:
        temp = get_temp()

        # Start the fan if the temperature has reached the limit and the fan
        # isn't already running.
        # NOTE: `fan.value` returns 1 for "on" and 0 for "off"
        if temp > ON_THRESHOLD and not fan.value:
            fan.on()
            fan_start_time = time.time()

        # Stop the fan if the fan is running and the temperature has dropped
        # to the OFF_THRESHOLD and the fan has been on for at least
        # the MIN_FAN_ON_TIME.
        elif fan.value and temp < OFF_THRESHOLD and time.time() - fan_start_time > MIN_FAN_ON_TIME:
            fan.off()
            fan_start_time = None  # Reset the fan start time

        time.sleep(SLEEP_INTERVAL)
