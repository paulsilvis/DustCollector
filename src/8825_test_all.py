import time
from distributor import Distributor
import atexit
import RPi.GPIO as GPIO

MOTORS = [1, 2, 3, 4]  # Motor IDs
RPM = 60
STEPS_PER_REV = 200
ROTATIONS = 5
TOTAL_STEPS = ROTATIONS * STEPS_PER_REV
STEP_INTERVAL_SEC = 60 / (RPM * STEPS_PER_REV)

print(f"Step interval: {STEP_INTERVAL_SEC:.8f} sec")

atexit.register(GPIO.cleanup)

def move_motors(dist, motors, direction):
    for motor in motors:
        dist.set_dir(motor, direction)
    print(f"Moving {ROTATIONS} rotations {'forward' if direction else 'backward'}...")
    for _ in range(TOTAL_STEPS):
        for motor in motors:
            dist.step(motor)
        time.sleep(STEP_INTERVAL_SEC)

def main():
	dist = Distributor()
	while True:
		# Enable all motors
		for motor in MOTORS:
			dist.set_enable(motor, True)

		try:
			move_motors(dist, MOTORS, direction=1)  # Forward
			move_motors(dist, MOTORS, direction=0)  # Backward
		except KeyboardInterrupt:
			print("\nInterrupted. Stopping motors.")
			break;

	for motor in MOTORS:
		dist.set_enable(motor, False)
	print("All motors disabled.")

if __name__ == "__main__":
    main()
