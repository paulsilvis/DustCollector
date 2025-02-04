"""Hardware CurrentSensor for detecting running machines"""

from sensor import Sensor


class CurrentSensor(Sensor):
    """Binary sensor -- ON or OFF."""

    def __init__(self, id):
        """Super keeps track of id and state."""
        super().__init__()

    def read(self):
        """Use the op-amp circuit to return ON or OFF."""
        return self.state  # tbd -- do what it says
