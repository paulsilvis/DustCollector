from smbus2 import SMBus
import time

I2C_BUS = 1
PCF_ADDR = 0x20    # adjust to your first PCF address

with SMBus(I2C_BUS) as bus:
    # All LEDs OFF initially
    bus.write_byte(PCF_ADDR, 0x00)
    print("All LEDs OFF")
    time.sleep(1)

    # Walk a single LED ON across all 8 bits

    while True:
	    for i in range(8):
	        pattern = 1 << i
	        bus.write_byte(PCF_ADDR, pattern)
	        print(f"LED {i} ON → Pattern: {pattern:08b}")
	        time.sleep(0.5)

	    # All LEDs ON
	    bus.write_byte(PCF_ADDR, 0xFF)
	    print("All LEDs ON")
	    time.sleep(1)

	    # All LEDs OFF again
	    bus.write_byte(PCF_ADDR, 0x00)
	    print("All LEDs OFF")
