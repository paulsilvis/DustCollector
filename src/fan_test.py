import RPi.GPIO as GPIO
import time


# Pin numbers
FAN1_PIN = 20
FAN2_PIN = 21

On = GPIO.LOW
Off = GPIO.HIGH

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN1_PIN, GPIO.OUT)
GPIO.setup(FAN2_PIN, GPIO.OUT)

try:
    while True:
        selection = input("Enter 0 (off), 1 (fan1), or 2 (fan2): ").strip()

        if selection == "0":
            GPIO.output(FAN1_PIN, Off)
            GPIO.output(FAN2_PIN, Off)
            print("Both fans OFF.\n")
        elif selection == "1":
            GPIO.output(FAN1_PIN, On)
            GPIO.output(FAN2_PIN, Off)
            print("Fan 1 ON, Fan 2 OFF.\n")
        elif selection == "2":
            GPIO.output(FAN1_PIN, Off)
            GPIO.output(FAN2_PIN, On)
            print("Fan 1 OFF, Fan 2 ON.\n")
        elif selection == "3":
            GPIO.output(FAN1_PIN, On)
            GPIO.output(FAN2_PIN, On)	    
            print("BOTH fans on\n")
        else:
            print("Invalid selection.\n")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
