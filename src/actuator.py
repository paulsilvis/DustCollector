from abc import ABC, abstractmethod


class Actuator(ABC):
    """Base class for actuators such as servo or linearactuator."""

    def __init__(self, id, name):
        """Save id and name"""
        self.id = id
        self.name = name

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass
