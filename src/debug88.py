#dist.bits = (1 << 13)  # STEP line

from distributor import Distributor
import time
import atexit
import RPi.GPIO as GPIO
atexit.register(GPIO.cleanup)

dist = Distributor()
dist.bits = (1 << 12)  # Set ONLY bit 12 HIGH
dist.flush()
print("Q4 (Chip2) should now be HIGH.")
time.sleep(10)
dist.bits = 0
dist.flush()
