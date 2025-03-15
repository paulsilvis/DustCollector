"""Module for controlling relays using Raspberry Pi GPIO."""

import RPi.GPIO as GPIO


class RelayController:
    """Controls a relay module connected to a GPIO pin."""

    def __init__(self, pin: int):
        """Initializes the relay controller.

        Args:
            pin (int): GPIO pin number.
        """
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.deactivate()

    def activate(self) -> None:
        """Activates the relay (turns it on)."""
        GPIO.output(self.pin, GPIO.HIGH)

    def deactivate(self) -> None:
        """Deactivates the relay (turns it off)."""
        GPIO.output(self.pin, GPIO.LOW)

    def cleanup(self) -> None:
        """Cleans up GPIO settings."""
        GPIO.cleanup(self.pin)
