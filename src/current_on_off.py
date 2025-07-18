import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# Set up I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADC instance
ads = ADS1115(i2c)

# Optionally set gain
ads.gain = 1  # ±4.096V

# Create analog input channel 0
chan0 = AnalogIn(ads, 0)

# Threshold voltage for ON/OFF
threshold = 0.025

# Start with unknown previous state
prev_state = None

while True:
    voltage = chan0.voltage
    if voltage is None:
        # Sometimes AnalogIn may return None if I2C glitches
        continue

    if voltage < threshold:
        current_state = "Off"
    else:
        current_state = "On"

    if current_state != prev_state:
        print(current_state)
        prev_state = current_state

    time.sleep(0.2)
