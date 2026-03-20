# Author
# Erick Sena Godinho - m320808

from time import sleep
from controller import Robot
from enum import Enum

TIME_STEP = 64
MAX_SPEED = 6.28
COUNTER_MAX = 5
COUNTER_STOP = 50
LINE_SENSOR_THRESHOLD = 600
COLLISION_THRESHOLD = 80

class State(Enum):
    FORWARD = "forward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    STOP = "stop"

speed = 1 * MAX_SPEED
current_state = State.TURN_RIGHT
leftSpeed = 0
rightSpeed = 0

# Initial status of the line sensor: updated by Webots via serial
line_left = False
line_center = False
line_right = False

# Variables to implement the line-following state machine
counter = 0
COUNTER_MAX = 5
COUNTER_STOP = 50

def update_sensor_status_esp(msg_bytes):
    """Update the line sensor status based on the received message."""
    
    global line_left, line_center, line_right
    
    msg_str = msg_bytes.decode('utf-8')
    
    line_left = msg_str[-4:-3] == '1'
    line_center = msg_str[-3:-2] == '1'
    line_right = msg_str[-2:-1] == '1'
        
def update_current_state_esp():
    """Logic to decide the robot's movement based on sensor data."""
    global current_state, counter

    # Decide action based on current state
    if current_state == State.FORWARD:
        counter = 0
        if line_left == 0 and line_center == 1 and line_right == 1:
            current_state = State.TURN_RIGHT
        elif line_left == 1 and line_center == 1 and line_right == 0:
            current_state = State.TURN_LEFT
        elif line_center == 0:
            current_state = State.FORWARD
        elif line_left == 1 and line_right == 1:
            current_state = State.TURN_LEFT

    elif current_state in [State.TURN_RIGHT, State.TURN_LEFT]:
        if counter >= COUNTER_MAX:
            current_state = State.FORWARD

    counter += 1

def control_motors(current_state):
    """Control the motor speeds based on the current state."""
    global leftSpeed, rightSpeed

    if current_state == State.FORWARD:
        leftSpeed = speed
        rightSpeed = speed
    elif current_state == State.TURN_RIGHT:
        leftSpeed = 0.5 * speed
        rightSpeed = 0.0
    elif current_state == State.TURN_LEFT:
        leftSpeed = 0.0
        rightSpeed = 0.5 * speed
    elif current_state == State.STOP:
        leftSpeed = 0.0
        rightSpeed = 0.0
    else:
        print(f"Unknown state: {current_state}")


def avoid_collision():
    """Check and handle potential collisions based on proximity sensors."""
    front_collision = any(ps[i].getValue() > COLLISION_THRESHOLD for i in [0, 1, 2, 5, 6, 7])
    back_collision = ps[3].getValue() > COLLISION_THRESHOLD or ps[4].getValue() > COLLISION_THRESHOLD

    if front_collision:
        return State.TURN_LEFT
    elif back_collision:
        return State.FORWARD

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
    
    update_sensor_status_esp(msg_bytes)

    update_current_state_esp()

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

