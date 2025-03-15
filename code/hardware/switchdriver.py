"""Module for reading switch states using Raspberry Pi GPIO."""

import RPi.GPIO as GPIO


class SwitchReader:
    """Reads the state of a switch connected to a GPIO pin."""

    def __init__(self, pin: int, pull_up: bool = True):
        """Initializes the switch reader.

        Args:
            pin (int): GPIO pin number.
            pull_up (bool): use an internal pull-up resistor? Default: True.
        """
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        pull = GPIO.PUD_UP if pull_up else GPIO.PUD_DOWN
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=pull)

    def is_pressed(self) -> bool:
        """Checks if the switch is pressed.

        Returns:
            bool: True if the switch is pressed, False otherwise.
        """
        return GPIO.input(self.pin) == GPIO.LOW

    def cleanup(self) -> None:
        """Cleans up GPIO settings."""
        GPIO.cleanup(self.pin)
