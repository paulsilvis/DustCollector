import time
from distributor import Distributor
import atexit
import RPi.GPIO as GPIO

MOTOR = 2
RPM = 60
STEPS_PER_REV = 200
STEP_INTERVAL_SEC = 60 / (RPM * STEPS_PER_REV) 
print(f"Step interval: {STEP_INTERVAL_SEC:.8f} sec")

atexit.register(GPIO.cleanup)

def main():
    dist = Distributor()
    dist.set_enable(MOTOR, True)
    dist.set_dir(MOTOR, 1)  # 1 = forward (can switch later)

    print(f"Motor {MOTOR} running at {RPM} RPM . Ctrl+C to stop.")
    try:
        while True:
            dist.step(MOTOR)
            time.sleep(STEP_INTERVAL_SEC)
    except KeyboardInterrupt:
        print("\nStopping motor.")
        dist.set_enable(MOTOR, False)

if __name__ == "__main__":
    main()
