# Author
# Erick Sena Godinho - m320808

from time import sleep
from controller import Robot
import serial

try:
    # Change the port parameter according to your system
    ser = serial.Serial(port='COM5', baudrate=115200, timeout=5)
except:
    print("Communication failed. Check the cable connections and serial settings 'port' and 'baudrate'.")
    raise

TIME_STEP = 64
MAX_SPEED = 6.28
COUNTER_MAX = 5
COUNTER_STOP = 50
LINE_SENSOR_THRESHOLD = 600
COLLISION_THRESHOLD = 80

# Use strings instead of IntEnum for states
FORWARD = "forward"
TURN_LEFT = "turn_left"
TURN_RIGHT = "turn_right"
STOP = "stop"

speed = 1 * MAX_SPEED
current_state = FORWARD
leftSpeed = 0
rightSpeed = 0

def control_motors(current_state):
    """Control the motor speeds based on the current state."""

    global leftSpeed, rightSpeed

    if current_state == FORWARD:
        leftSpeed = speed
        rightSpeed = speed
    elif current_state == TURN_RIGHT:
        leftSpeed = 0.5 * speed
        rightSpeed = 0.0
    elif current_state == TURN_LEFT:
        leftSpeed = 0.0
        rightSpeed = 0.5 * speed
    elif current_state == STOP:
        leftSpeed = 0.0
        rightSpeed = 0.0
    else:
        print(current_state)


def avoid_collision():
    """Check and handle potential collisions based on proximity sensors."""
    front_collision = any(ps[i].getValue() > COLLISION_THRESHOLD for i in [0, 1, 2, 5, 6, 7])
    back_collision = ps[3].getValue() > COLLISION_THRESHOLD or ps[4].getValue() > COLLISION_THRESHOLD

    if front_collision:
        return TURN_LEFT
    elif back_collision:
        return FORWARD

    return None


# Initialization
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Initialize devices
ps = [robot.getDevice(f'ps{i}') for i in range(8)]
gs = [robot.getDevice(f'gs{i}') for i in range(3)]

for sensor in ps + gs:
    sensor.enable(timestep)

leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))
leftMotor.setVelocity(0.0)
rightMotor.setVelocity(0.0)

# Main loop
while robot.step(timestep) != -1:

    # ----- See -----
    gsValues = [gs[i].getValue() for i in range(3)]
    line_left = gsValues[0] > LINE_SENSOR_THRESHOLD
    line_center = gsValues[1] > LINE_SENSOR_THRESHOLD
    line_right = gsValues[2] > LINE_SENSOR_THRESHOLD

    message = ''.join(['1' if sensor else '0' for sensor in [line_left, line_center, line_right]])
    msg_bytes = bytes(message + '\n', 'UTF-8')
    
    # Send message to the microcontroller
    ser.write(msg_bytes)

    # ----- Think -----
    # Serial communication: if something is received,
    # then update the current state
    if ser.in_waiting:
        value = str(ser.readline(), 'UTF-8')  # Remove newline and other end characters
        value = value[:-2]
        current_state = value

    # Avoid collisions if necessary
    collision_state = avoid_collision()
    if collision_state:
        current_state = collision_state

    # Control motors based on the current state
    control_motors(current_state)
    leftMotor.setVelocity(leftSpeed)
    rightMotor.setVelocity(rightSpeed)

    # Debugging output
    print(f'Sensor message: {msg_bytes} - Current state: {current_state}')

ser.close()
