from smbus2 import SMBus


class PCF8574_in:
    def __init__(self, address=0x20, bus_num=1):
        self.address = address
        self.bus = SMBus(bus_num)
        # Write 0xFF to set all pins to input mode (float high)
        self.bus.write_byte(self.address, 0xFF)

    def read_pin(self, pin_number):
        """Returns 0 if pulled low, 1 if high (unpressed)."""
        if not 0 <= pin_number <= 7:
            raise ValueError("pin_number must be 0–7")
        value = self.bus.read_byte(self.address)
        return (value >> pin_number) & 1

    def read_all(self):
        """Returns raw 8-bit input byte (1 = high, 0 = low)."""
        return self.bus.read_byte(self.address)
