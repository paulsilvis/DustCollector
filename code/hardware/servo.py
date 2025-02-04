"""Hardware Servo Actuator"""

from actuator import Actuator


class Servo(Actuator):
    """Servo actuator, do some PWM stuff."""

    def __init__(self, id, name):
        super.__init__(id, name)

    def open(self):
        """Open."""
        # -- actually do it!
        print("actuator open")

    def close(self):
        """Close."""
        # -- actually do it!
        print("actuator closed")
