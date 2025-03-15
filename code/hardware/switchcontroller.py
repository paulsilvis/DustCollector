import smbus2
import time


class SwitchController:
    """Class to handle 16 switch inputs using MCP23017
    with efficient XOR-based change detection.
    """

    def __init__(self, address=0x20, bus_num=1, debounce_time=0.02):
        """
        Initialize the MCP23017 for switch input.

        :param address: I2C address of the MCP23017 (default: 0x20)
        :param bus_num: I2C bus number (default: 1)
        :param debounce_time: Debounce delay in seconds (default: 0.02s)
        """
        self.address = address
        self.bus = smbus2.SMBus(bus_num)
        self.debounce_time = debounce_time

        # Configure all pins as inputs (IODIR = 0xFF)
        self.bus.write_byte_data(self.address, 0x00, 0xFF)  # IODIRA (Port A)
        self.bus.write_byte_data(self.address, 0x01, 0xFF)  # IODIRB (Port B)

        # Enable pull-up resistors for both ports (GPPU = 0xFF)
        self.bus.write_byte_data(self.address, 0x0C, 0xFF)  # GPPUA (Port A)
        self.bus.write_byte_data(self.address, 0x0D, 0xFF)  # GPPUB (Port B)

        # Store last stable switch states (initialized to all unpressed)
        self.last_states = 0xFFFF  # All 16 bits high (pull-ups active)

    def _read_raw_states(self):
        """
        Reads both GPIO ports and returns a combined 16-bit value.

        :return: 16-bit integer where each bit represents a switch state.
        """
        value_a = self.bus.read_byte_data(self.address, 0x12)  # GPIOA
        value_b = self.bus.read_byte_data(self.address, 0x13)  # GPIOB
        return (value_b << 8) | value_a  # Combine ports

    def read_switch(self, switch_id):
        """
        Reads switch n, debounces if needed, and returns its stable state.

        :param switch_id: Switch ID (0-15)
        :return: True if the switch is pressed, False otherwise.
        """
        if not 0 <= switch_id < 16:
            raise ValueError("Switch ID must be between 0 and 15")

        # Read all switch states
        new_states = self._read_raw_states()

        # Detect if any switch has changed using XOR
        if new_states ^ self.last_states:  # If any bit has changed
            time.sleep(self.debounce_time)  # Wait for debounce period
            debounced_states = self._read_raw_states()  # reread for stability

            # Only update last_states if still the same after debounce
            if debounced_states == new_states:
                self.last_states = debounced_states

        # Return the stable state of the requested switch (Active LOW)
        return not bool(self.last_states & (1 << switch_id))


# Example usage
if __name__ == "__main__":
    switches = SwitchController()

    while True:
        for i in range(16):
            if switches.read_switch(i):  # Call read_switch() for each switch
                print(f"Switch {i} is pressed")

        time.sleep(0.1)  # Small delay to avoid excessive polling
