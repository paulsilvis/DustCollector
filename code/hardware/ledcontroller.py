import smbus2

class LEDController:
    def __init__(self, address=0x20, bus_num=1):
        self.address = address
        self.bus = smbus2.SMBus(bus_num)

        # Configure all pins (A & B) as outputs (IODIR = 0x00)
        self.bus.write_byte_data(self.address, 0x00, 0x00)  # IODIRA (Port A)
        self.bus.write_byte_data(self.address, 0x01, 0x00)  # IODIRB (Port B)

        # Initialize LED states (both ports OFF)
        self.led_states = { 'A': 0x00, 'B': 0x00 }

    def led_on(self, id):
        """Turns on an LED (0-15) by setting the corresponding bit in OLAT register."""
        if 0 <= id < 8:
            port, reg = 'A', 0x14  # OLATA
        elif 8 <= id < 16:
            port, reg = 'B', 0x15  # OLATB
            id -= 8  # Adjust ID for Port B (GPB0-GPB7)
        else:
            raise ValueError("LED ID must be between 0-15")

        self.led_states[port] |= (1 << id)
        self.bus.write_byte_data(self.address, reg, self.led_states[port])

    def led_off(self, id):
        """Turns off an LED (0-15) by clearing the corresponding bit in OLAT register."""
        if 0 <= id < 8:
            port, reg = 'A', 0x14  # OLATA
        elif 8 <= id < 16:
            port, reg = 'B', 0x15  # OLATB
            id -= 8  # Adjust ID for Port B (GPB0-GPB7)
        else:
            raise ValueError("LED ID must be between 0-15")

        self.led_states[port] &= ~(1 << id)
        self.bus.write_byte_data(self.address, reg, self.led_states[port])

# Example usage
if __name__ == "__main__":
    leds = MCP23017()
    leds.led_on(0)   # Turn on LED at GPA0
    leds.led_on(8)   # Turn on LED at GPB0
    leds.led_off(0)  # Turn off LED at GPA0
    leds.led_off(8)  # Turn off LED at GPB0
