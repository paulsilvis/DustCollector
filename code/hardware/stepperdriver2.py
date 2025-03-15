import time
import board
import busio
import adafruit_mcp230xx

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize MCP23017 at default I2C address (0x20)
mcp = adafruit_mcp230xx.MCP23017(i2c)

# Assign stepper motor pins
STEPPERS = [
    {"STEP": mcp.get_pin(8), "DIR": mcp.get_pin(9)},  # Stepper 1
    {"STEP": mcp.get_pin(10), "DIR": mcp.get_pin(11)},  # Stepper 2 (if needed)
]

# Assign limit switch pins
LIMIT_SWITCHES = {
    "closed": mcp.get_pin(0),  # Fully closed position
    "open": mcp.get_pin(1),  # Fully open position
}

# Configure MCP23017 pins
for stepper in STEPPERS:
    stepper["STEP"].switch_to_output(value=False)
    stepper["DIR"].switch_to_output(value=False)

for switch in LIMIT_SWITCHES.values():
    switch.switch_to_input(pull=adafruit_mcp230xx.Pull.UP)  # Pull-up resistor

# Motion parameters
STEP_DELAY = 0.005  # Time per step
HOMING_SPEED = 0.01  # Slower speed for homing
TIMEOUT_SECONDS = 6  # Auto shutoff timeout if no limit switch is triggered

def stepper_move(stepper_index, steps, direction, delay, stop_at_limit=None):
    """
    Move stepper motor a specific number of steps with timeout, safety checks.
    - stepper_index: Index of the stepper motor
    - steps: Number of steps to move
    - direction: 1 for forward, 0 for backward
    - delay: Step delay time
    - stop_at_limit: Limit switch pin to check (stops if triggered)
    """
    stepper = STEPPERS[stepper_index]
    stepper["DIR"].value = direction  # Set direction

    start_time = time.time()  # Track time to prevent jamming

    for _ in range(steps):
        stepper["STEP"].value = True
        time.sleep(delay / 2)
        stepper["STEP"].value = False
        time.sleep(delay / 2)

        # If a limit switch is defined, stop if it activates
        if stop_at_limit and not stop_at_limit.value:
            print(f"Stepper {stepper_index} stopped by limit switch.")
            return

        # Auto shutoff if timeout occurs
        if time.time() - start_time > TIMEOUT_SECONDS:
            print(f"Stepper {stepper_index} timed out! Stopping movement.")
            return

def home_stepper(stepper_index):
    """Move stepper toward the closed limit switch for homing."""
    stepper = STEPPERS[stepper_index]
    print(f"Homing Stepper {stepper_index}...")

    stepper["DIR"].value = 0  # Move toward home

    start_time = time.time()

    while LIMIT_SWITCHES["closed"].value:  # Wait for limit switch press
        stepper["STEP"].value = True
        time.sleep(HOMING_SPEED / 2)
        stepper["STEP"].value = False
        time.sleep(HOMING_SPEED / 2)

        if time.time() - start_time > TIMEOUT_SECONDS:
            print(f"Stepper {stepper_index} homing failed! Timeout.")
            return

    print(f"Stepper {stepper_index} Home Position Reached.")
    time.sleep(0.5)  # Short pause

try:
    # Home each stepper motor
    for i in range(len(STEPPERS)):
        home_stepper(i)

    # Move each stepper to open position
    for i in range(len(STEPPERS)):
        print(f"Opening Stepper {i} Blast Gate...")
        stepper_move(i, 2000, 1, STEP_DELAY, 
                    stop_at_limit=LIMIT_SWITCHES["open"])
        time.sleep(2)

    # Move each stepper to closed position
    for i in range(len(STEPPERS)):
        print(f"Closing Stepper {i} Blast Gate...")
        stepper_move(i, 2000, 0, STEP_DELAY, 
                                stop_at_limit=LIMIT_SWITCHES["closed"])
        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping...")
