import RPi.GPIO as GPIO
import time

# Pin numbers
FAN1_PIN = 20
FAN2_PIN = 21

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN1_PIN, GPIO.OUT)
GPIO.setup(FAN2_PIN, GPIO.OUT)

# ON and OFF symbols
ON = GPIO.LOW
OFF = GPIO.HIGH

def get_cpu_temp_fahrenheit():
    """Reads Pi CPU temp in Fahrenheit."""
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp_str = f.readline().strip()
    temp_c = float(temp_str) / 1000.0
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_f

try:
    # Prompt for setpoint once
    setpoint_str = input("Enter CPU temp setpoint in °F: ").strip()
    setpoint = float(setpoint_str)

    while True:
        # Read CPU temp
        temp_f = get_cpu_temp_fahrenheit()
        print(f"CPU Temperature: {temp_f:.2f} °F")

        # Compare and control fan2
        if temp_f > setpoint:
            GPIO.output(FAN2_PIN, ON)
            print("Fan 2 ON.")
        else:
            GPIO.output(FAN2_PIN, OFF)
            print("Fan 2 OFF.")

        time.sleep(2)  # adjust polling interval as you like

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
