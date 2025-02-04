"""Servo Actuator Mockup"""

from actuator import Actuator


class Servo(Actuator):
    """Dummy actuator, just prints stuff."""

    def __init__(self, id, name):
        super.__init__(id, name)

    def open(self):
        """Open."""
        print("actuator open")

    def close(self):
        """Close."""
        print("actuator closed")
