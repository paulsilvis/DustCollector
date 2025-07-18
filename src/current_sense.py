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
ads.gain = 1

# Create AnalogIn channels
channels = [AnalogIn(ads, i) for i in range(4)]

while True:
    for i, channel in enumerate(channels):
        print(f"Channel {i}: raw={channel.value}, voltage={channel.voltage:.6f} V")
    print("-" * 40)
    time.sleep(1)
