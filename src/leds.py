from smbus2 import SMBus

I2C_BUS = 1
PCF_ADDR = 0x20    # replace with your PCF8574 address

with SMBus(I2C_BUS) as bus:
    while True:
        inp = input("Enter LED bit number (0-7), or q to quit: ").strip()
        if inp.lower() == 'q':
            # Turn all LEDs off before exiting
            bus.write_byte(PCF_ADDR, 0x00)
            print("All LEDs OFF. Exiting.")
            break

        try:
            bit = int(inp)
            if 0 <= bit <= 7:
                pattern = 1 << bit
                bus.write_byte(PCF_ADDR, pattern)
                print(f"Set bit {bit}: pattern {pattern:08b}")
            else:
                print("Number out of range (0-7).")
        except ValueError:
            print("Invalid input. Enter a number or 'q'.")
