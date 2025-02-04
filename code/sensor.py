"""Sensor base class"""

from abc import ABC, abstractmethod
from enum import Enum


# Enums for states
class SensorState(Enum):
    """Binary sensors only for now."""

    ON = "ON"
    OFF = "OFF"


class Sensor(ABC):
    """Abstract base class for sensors."""

    def __init__(self, id, name):
        """Keep track of id and state"""
        self.id = id
        self.name = name
        self.state = SensorState.OFF

    @abstractmethod
    def read(self):
        """Returns either ON or OFF, indicating the machine's state."""
        pass
