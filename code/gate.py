"""Base class for Gate."""

from enum import Enum
from timer import Timer


class GateState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class OperatingState(Enum):
    S0 = "MACHINE_OFF_GATE_CLOSED_MOTOR_OFF"
    S1 = "MACHINE_ON_GATE_OPEN_MOTOR_ON"
    S2 = "MACHINE_OFF_GATE_OPEN_MOTOR_ON_WAITING"


class Gate:
    """A blast-gate"""

    def __init__(self, id, name, tool, actuator):
        self.id = id
        self.name = name
        self.tool = tool
        self.actuator = actuator
        self.state = GateState.CLOSED
        self.op_state = OperatingState.S0
        self.timer = Timer()

    def close(self):
        """Close the gate."""
        self.actuator.close()
        self.state = GateState.CLOSED
        print(f"Gate {self.name} closed")

    def open(self):
        """Open the gate"""
        self.actuator.open()
        self.state = GateState.OPEN
        print(f"Gate {self.name} opened")
