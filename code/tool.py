"""A machine Tool class."""

from enum import Enum


class ToolState(Enum):
    ON = "ON"
    OFF = "OFF"


class Tool:
    """Something like a tablesaw, that has an associated get and sensor."""

    def __init__(self, gate, sensor):
        """Starting out OFF."""
        self.gate = gate
        self.sensor = sensor
        self.state = ToolState.OFF

    def get_state(self):
        """Save and return current sensor ON or OFF state."""
        self.state = self.sensor.read()
        return self.state
