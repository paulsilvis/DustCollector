import time

from src.actuator import Actuator

class StepperActuator8825(Actuator):
    """Stepper actuator using DRV8825 or TMC2209 via MCP23017.

    Includes limit switch integration and homing behavior.

    Note:
        The driver’s microstepping mode is configured via physical DIP
        switches or jumpers (MS1, MS2, MS3). Be sure to adjust
        `steps_per_action` to match the effective step size.

        Example:
            Full step (1x):     steps_per_action = 900
            1/8 microstepping:  steps_per_action = 900 * 8 = 7200
    """

    def __init__(
        self,
        id,
        name,
        mcp,
        dir_pin,
        step_pin,
        en_pin,
        limit_switch_open_id,
        limit_switch_closed_id,
        switch_controller,
        steps_per_action=900,
        delay=0.002,
    ):
        """
        Initialize a stepper actuator.

        :param id: Unique actuator ID.
        :param name: Descriptive name for the actuator.
        :param mcp: MCP23017 instance.
        :param dir_pin: MCP pin for DIR.
        :param step_pin: MCP pin for STEP.
        :param en_pin: MCP pin for EN (active LOW).
        :param limit_switch_open_id: Switch ID for open limit.
        :param limit_switch_closed_id: Switch ID for closed limit.
        :param switch_controller: SwitchController instance.
        :param steps_per_action: Max steps to take if limit not hit.
        :param delay: Delay between steps (in seconds).
        """
        super().__init__(id, name)
        self.mcp = mcp
        self.dir_pin = self.mcp.get_pin(dir_pin)
        self.step_pin = self.mcp.get_pin(step_pin)
        self.en_pin = self.mcp.get_pin(en_pin)
        self.switch_controller = switch_controller
        self.limit_switch_open_id = limit_switch_open_id
        self.limit_switch_closed_id = limit_switch_closed_id
        self.steps_per_action = steps_per_action
        self.delay = delay
        self.position = "unknown"

        self.dir_pin.direction = True
        self.step_pin.direction = True
        self.en_pin.direction = True
        self.disable()
        self.home()

    def enable(self):
        """Enable stepper driver (EN active LOW)."""
        self.en_pin.value = False

    def disable(self):
        """Disable stepper driver."""
        self.en_pin.value = True

    def move(self, direction, target_switch_id):
        """Move in direction until limit switch is hit or max steps."""
        self.dir_pin.value = direction
        self.enable()
        step_counter = 0

        while step_counter < self.steps_per_action:
            if self.switch_controller.read_switch(target_switch_id):
                print(f"{self.name} limit switch {target_switch_id} hit.")
                break

            self.step_pin.value = True
            time.sleep(self.delay)
            self.step_pin.value = False
            time.sleep(self.delay)
            step_counter += 1

        self.disable()

    def open(self):
        """Move actuator to the open position."""
        print(f"{self.name} opening...")
        self.move(direction=1, target_switch_id=self.limit_switch_open_id)
        self.position = "open"

    def close(self):
        """Move actuator to the closed position."""
        print(f"{self.name} closing...")
        self.move(direction=0, target_switch_id=self.limit_switch_closed_id)
        self.position = "closed"

    def home(self):
        """Home actuator to the closed position on startup."""
        print(f"{self.name} homing to 'closed' position...")
        self.dir_pin.value = 0
        self.enable()
        while not self.switch_controller.read_switch(
            self.limit_switch_closed_id
        ):
            self.step_pin.value = True
            time.sleep(self.delay)
            self.step_pin.value = False
            time.sleep(self.delay)
        self.disable()
        self.position = "closed"
        print(f"{self.name} homed successfully to CLOSED position.")
