"""Module for controlling LEDs using Raspberry Pi GPIO."""

import RPi.GPIO as GPIO


class LEDController:
    """Controls an LED connected to a GPIO pin."""

    def __init__(self, pin: int):
        """Initializes the LED controller.

        Args:
            pin (int): GPIO pin number.
        """
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.off()

    def on(self) -> None:
        """Turns the LED on."""
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self) -> None:
        """Turns the LED off."""
        GPIO.output(self.pin, GPIO.LOW)

    def toggle(self) -> None:
        """Toggles the LED state."""
        GPIO.output(self.pin, not GPIO.input(self.pin))

    def cleanup(self) -> None:
        """Cleans up GPIO settings."""
        GPIO.cleanup(self.pin)
