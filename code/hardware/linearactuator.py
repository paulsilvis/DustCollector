"""Hardware Linear Actuator"""

from actuator import Actuator


class LinearActuator(Actuator):
    """Linear actuator."""

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
