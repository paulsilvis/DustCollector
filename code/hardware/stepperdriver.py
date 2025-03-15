"""Stepper Controller for Greartisan 12V DC 100RPM motor using an
L298N motor driver with PWM speed control and direction reversal.
"""

import time
import RPi.GPIO as GPIO


# Define GPIO pins
ENA = 18  # PWM control
IN1 = 23  # Direction control 1
IN2 = 24  # Direction control 2


def setup_gpio():
    """Initialize GPIO pins and PWM."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ENA, GPIO.OUT)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)

    global pwm
    pwm = GPIO.PWM(ENA, 1000)  # 1kHz frequency
    pwm.start(0)  # Start with 0% duty cycle (motor off)


def motor_forward(speed: int = 100) -> None:
    """
    Run motor forward at a given speed (0-100%).

    :param speed: Speed percentage (0-100)
    """
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(speed)


def motor_backward(speed: int = 100) -> None:
    """
    Run motor backward at a given speed (0-100%).

    :param speed: Speed percentage (0-100)
    """
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(speed)


def motor_stop() -> None:
    """Stop motor."""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)


def cleanup_gpio() -> None:
    """Cleanup GPIO on exit."""
    motor_stop()
    GPIO.cleanup()


def main():
    """Run motor test sequence."""
    setup_gpio()
    try:
        while True:
            print("Motor Forward")
            motor_forward(75)  # Run at 75% speed
            time.sleep(3)

            print("Motor Stop")
            motor_stop()
            time.sleep(2)

            print("Motor Backward")
            motor_backward(50)  # Run at 50% speed
            time.sleep(3)

            print("Motor Stop")
            motor_stop()
            time.sleep(2)

    except KeyboardInterrupt:
        print("Stopping motor...")
        cleanup_gpio()


if __name__ == "__main__":
    main()
