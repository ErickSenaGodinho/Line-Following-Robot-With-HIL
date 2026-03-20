# Author
# Erick Sena Godinho - m320808

# Implements communication with Webots via Serial over USB.
# Works with the "line_following_with_HIL" controller in Webots.

from machine import Pin, UART
from time import sleep

# Set serial to UART1 using the same pins as UART0 to communicate via USB
uart = UART(1, 115200, tx=1, rx=3)

# Initial status of the line sensor: updated by Webots via serial
line_left = False
line_center = False
line_right = False

# Variables to implement the line-following state machine
current_state = "forward"
state_updated = False
counter = 0
COUNTER_MAX = 5
COUNTER_STOP = 50


def update_sensor_status(msg_str):
    """Update the line sensor status based on the received message."""
    global line_left, line_center, line_right

    line_left = msg_str[-4:-3] == "1"
    line_center = msg_str[-3:-2] == "1"
    line_right = msg_str[-2:-1] == "1"


def update_current_state():
    """Logic to decide the robot's movement based on sensor data."""
    global current_state, counter, state_updated

    # Decide action based on current state
    if current_state == "forward":
        counter = 0
        if line_left == 0 and line_center == 1 and line_right == 1:
            current_state = "turn_right"
            state_updated = True
        elif line_left == 1 and line_center == 1 and line_right == 0:
            current_state = "turn_left"
            state_updated = True
        elif line_center == 0:
            current_state = "forward"
        elif line_left == 1 and line_right == 1:
            current_state = "turn_left"
            state_updated = True

    elif current_state in ["turn_right", "turn_left"]:
        if counter >= COUNTER_MAX:
            current_state = "forward"
            state_updated = True

    counter += 1


while True:
    ##################   See   ###################

    # Check if anything was received via serial to update sensor status
    if uart.any():
        msg_bytes = uart.read()  # Read all received messages
        msg_str = msg_bytes.decode("utf-8")
        # Convert to string
        # Ignore old messages (Webots can send faster than the ESP32 can process)
        # Then split them in the same order used in Webots and update sensor status

        update_sensor_status(msg_str)

    update_current_state()

    ##################   Act   ###################

    # Send the new state when updated
    if state_updated:
        uart.write(current_state + "\n")
        state_updated = False

    counter += 1  # increment counter
    sleep(0.02)  # wait 0.02 seconds
