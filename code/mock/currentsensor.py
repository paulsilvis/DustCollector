"""Mock CurrentSensor for testing"""

from sensor import Sensor


class CurrentSensor(Sensor):
    """Binary sensor -- ON or OFF."""

    def __init__(self, id):
        """Super keeps track of id and state."""
        super().__init__()

    def read(self):
        """Simulate reading from a current sensor."""
        return self.state  # somebody else will have set this for the mock
