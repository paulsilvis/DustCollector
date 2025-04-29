import spidev
import time
import atexit



# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0
spi.max_speed_hz = 1000000

# GPIO latch pin (595 RCLK)
import RPi.GPIO as GPIO
atexit.register(GPIO.cleanup)
LATCH_PIN = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(LATCH_PIN, GPIO.OUT)
GPIO.output(LATCH_PIN, 0)

def latch():
    GPIO.output(LATCH_PIN, 0)
    time.sleep(0.000001)
    GPIO.output(LATCH_PIN, 1)
    time.sleep(0.000001)
    GPIO.output(LATCH_PIN, 0)

try:
    while True:
        for i in range(16):
            value = 1 << i
            byte1 = value & 0xFF      # chip2 (low byte)
            byte2 = (value >> 8) & 0xFF  # chip1 (high byte)
            spi.xfer2([byte2, byte1])
            latch()
            #time.sleep(0.2)
except KeyboardInterrupt:
    spi.xfer2([0, 0])
    latch()
    GPIO.cleanup()
