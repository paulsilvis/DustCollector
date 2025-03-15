import time
import board
import busio
import adafruit_mcp230xx


class StepperController:
    """Manages stepper motors using an MCP23017 I/O expander over I2C."""

    def __init__(self, i2c_address, stepper_names):
        """
        Initialize the MCP23017 expander for multiple stepper motors.
        :param i2c_address: I2C address of the MCP23017
        :param stepper_names: List of names for each stepper motor
        """
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.mcp = adafruit_mcp230xx.MCP23017(self.i2c, address=i2c_address)
        self.steppers = {}  # Store stepper configurations

        # Assign bit positions dynamically for each stepper
        bit_position = 8  # Start at GPB0 for STEP/DIR pins
        limit_switch_position = 0  # Start at GPA0 for limit switches

        for name in stepper_names:
            if bit_position + 1 > 15 or limit_switch_position + 1 > 7:
                raise ValueError(f"Too many steppers at {i2c_address}")

            self.steppers[name] = {
                "STEP": self.mcp.get_pin(bit_position),
                "DIR": self.mcp.get_pin(bit_position + 1),
                "CLOSED_LIMIT": self.mcp.get_pin(
                    limit_switch_position
                ),  # Closed limit switch
                "OPEN_LIMIT": self.mcp.get_pin(
                    limit_switch_position + 1
                ),  # Open limit switch
            }
            bit_position += 2  # Move to next available bit for STEP/DIR
            limit_switch_position += (
                2  # Move to next available bit for limit switches
            )

        # Configure all pins
        for stepper in self.steppers.values():
            stepper["STEP"].switch_to_output(value=False)
            stepper["DIR"].switch_to_output(value=False)
            stepper["CLOSED_LIMIT"].switch_to_input(
                pull=adafruit_mcp230xx.Pull.UP
            )  # Pull-up enabled
            stepper["OPEN_LIMIT"].switch_to_input(
                pull=adafruit_mcp230xx.Pull.UP
            )

        print(f"StepperController initialized at I2C address {i2c_address}")

    def stepper_move(
        self, stepper_name, steps, direction, delay, stop_at_limit=None
    ):
        """
        Move a stepper motor a specific number of steps with auto shutoff.
        :param stepper_name: Name of the stepper motor to move
        :param steps: Number of steps to move
        :param direction: 1 for forward (open), 0 for backward (close)
        :param delay: Step delay time
        :param stop_at_limit: "OPEN_LIMIT" or "CLOSED_LIMIT" for stopping
        """
        if stepper_name not in self.steppers:
            raise ValueError(f"Unknown stepper: {stepper_name}")

        stepper = self.steppers[stepper_name]
        stepper["DIR"].value = direction  # Set direction

        start_time = time.time()  # Track time for timeout

        for _ in range(steps):
            stepper["STEP"].value = True
            time.sleep(delay / 2)
            stepper["STEP"].value = False
            time.sleep(delay / 2)

            # If a limit switch is defined, stop if triggered
            if stop_at_limit and not stepper[stop_at_limit].value:
                print(f"Stepper {stepper_name} stopped by ({stop_at_limit}).")
                return

            # Auto shutoff if timeout occurs
            if time.time() - start_time > 6:
                print(f"Stepper {stepper_name} timed out! Stopping movement.")
                return

    def open(self, stepper_name):
        self.move_stepper_adaptive(stepper_name, 200, 20, 2, 1)

    def close(self, stepper_name):
        self.move_stepper_adaptive(stepper_name, 200, 20, 2, 0)

    def move_stepper_adaptive(self, stepper_name, steps,
                              fast_rate, slow_rate, direction):
        """
        Move a stepper motor, slowing down near the limit switch.
        :param controller: StepperController instance
        :param stepper_name: Name of the stepper motor
        :param steps: Total number of steps to move
        :param fast_rate: Step rate (steps/sec) when far from limit switch
        :param slow_rate: Step rate (steps/sec) when close to limit switch
        :param direction: 1 for forward (open), 0 for backward (close)
        """
        if stepper_name not in self.steppers:
            raise ValueError(f"Unknown stepper: {stepper_name}")

        stepper = self.steppers[stepper_name]
        stepper["DIR"].value = direction  # Set movement direction

        # Determine which limit switch to monitor
        limit_switch = (stepper["OPEN_LIMIT"] if direction == 1
                        else stepper["CLOSED_LIMIT"])

        for step in range(steps):
            # Check if the stepper is near the limit switch (last 10% of steps)
            if step > steps * 0.9:  # Slow down when within last 10% of travel
                step_delay = 1.0 / slow_rate
            else:
                step_delay = 1.0 / fast_rate

            stepper["STEP"].value = True
            time.sleep(step_delay / 2)
            stepper["STEP"].value = False
            time.sleep(step_delay / 2)

            # Stop early if the limit switch is triggered
            if not limit_switch.value:
                print(f"Stepper {stepper_name} stopped by limit switch.")
                return

    def home_stepper(self, stepper_name):
        """
        Move a stepper to its closed position using its dedicated limit switch.
        :param stepper_name: Name of the stepper motor to home
        """
        if stepper_name not in self.steppers:
            raise ValueError(f"Unknown stepper: {stepper_name}")

        stepper = self.steppers[stepper_name]
        print(f"Homing Stepper {stepper_name}...")

        stepper["DIR"].value = 0  # Move toward home (closed position)
        start_time = time.time()

        while stepper[
            "CLOSED_LIMIT"
        ].value:  # Wait for closed limit switch press
            stepper["STEP"].value = True
            time.sleep(0.01)
            stepper["STEP"].value = False
            time.sleep(0.01)

            if time.time() - start_time > 6:
                print(f"Stepper {stepper_name} homing failed! Timeout.")
                return

        print(f"Stepper {stepper_name} Home Position Reached.")
        time.sleep(0.5)  # Short pause


# Example Usage with Two MCP23017s
try:
    # Initialize controllers for different MCP23017s
    controller_1 = StepperController(
        i2c_address=0x20, stepper_names=["Gate1", "Gate2"]
    )
    controller_2 = StepperController(
        i2c_address=0x21, stepper_names=["Gate3", "Gate4"]
    )

    # Home all stepper motors
    for gate in ["Gate1", "Gate2"]:
        controller_1.home_stepper(gate)

    for gate in ["Gate3", "Gate4"]:
        controller_2.home_stepper(gate)

    # Move each stepper to open position
    for gate in ["Gate1", "Gate2"]:
        controller_1.stepper_move(
            gate,
            2000,
            1,
            0.005,
            stop_at_limit="OPEN_LIMIT",
        )
        time.sleep(2)

    for gate in ["Gate3", "Gate4"]:
        controller_2.stepper_move(
            gate,
            2000,
            1,
            0.005,
            stop_at_limit="OPEN_LIMIT",
        )
        time.sleep(2)

    # Move each stepper to closed position
    for gate in ["Gate1", "Gate2"]:
        controller_1.stepper_move(
            gate,
            2000,
            0,
            0.005,
            stop_at_limit="CLOSED_LIMIT",
        )
        time.sleep(2)

    for gate in ["Gate3", "Gate4"]:
        controller_2.stepper_move(
            gate,
            2000,
            0,
            0.005,
            stop_at_limit="CLOSED_LIMIT",
        )
        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping...")
