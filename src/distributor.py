import time
import spidev
import RPi.GPIO as GPIO

class Distributor:
    """
    Controls four DRV8825 stepper drivers via two chained 74HC595 shift registers.

    Bit layout is based on physical pin mapping:
    - High byte (bits 15–8) → Chip2 (rotated 180°)
    - Low byte (bits 7–0)   → Chip1 (upright)
    - Data sent MSB first (bit 15 down to bit 0)
    """

    MOTOR_MAP = {
        1: {'en': 12, 'step': 13, 'dir': 14},
        2: {'en': 9, 'step': 10, 'dir': 11},
        3: {'en': 4, 'step':  5, 'dir': 6},
        4: {'en': 1, 'step':  2, 'dir': 3},
    }

    def __init__(self, spi_bus=0, spi_device=0, spi_speed=1000000):
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = spi_speed
        GPIO.setmode(GPIO.BCM)
        self.LATCH_PIN = 25  # or whatever GPIO you want to use
        GPIO.setup(self.LATCH_PIN, GPIO.OUT)
        GPIO.output(self.LATCH_PIN, GPIO.LOW)
        self.bits = 0x0000
        self.flush()
        

    def flush(self):
        high = (self.bits >> 8) & 0xFF
        low = self.bits & 0xFF
        self.spi.xfer2([high, low])
        GPIO.output(self.LATCH_PIN, GPIO.HIGH)
        time.sleep(0.000001)  # 1 µs
        GPIO.output(self.LATCH_PIN, GPIO.LOW)        

    def _bit_set(self, bitnum, value):
        if value:
            self.bits |= (1 << bitnum)
        else:
            self.bits &= ~(1 << bitnum)

    def set_dir(self, motor, direction):
        if motor not in self.MOTOR_MAP:
            raise ValueError(f"Invalid motor ID: {motor}")
        bitnum = self.MOTOR_MAP[motor]['dir']
        self._bit_set(bitnum, direction)
        self.flush()

    def set_enable(self, motor, enable):
        if motor not in self.MOTOR_MAP:
            raise ValueError(f"Invalid motor ID: {motor}")
        bitnum = self.MOTOR_MAP[motor]['en']
        self._bit_set(bitnum, not enable)  # active-low
        self.flush()

    def step(self, motor, pulse_us=20):
        if motor not in self.MOTOR_MAP:
            raise ValueError(f"Invalid motor ID: {motor}")
        bitnum = self.MOTOR_MAP[motor]['step']
        self._bit_set(bitnum, 1)
        self.flush()
        time.sleep(pulse_us / 1_000_000)
        #time.sleep(1)
        self._bit_set(bitnum, 0)
        self.flush()
