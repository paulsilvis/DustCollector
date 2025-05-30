import board
import busio
import time
from adafruit_mcp230xx.mcp23017 import MCP23017
from digitalio import Direction

class MCP23017_in:
    def __init__(self, address=0x20):
        # Initialize I2C and the MCP chip
        self.i2c = busio.I2C(board.SCL, board.SDA)
        while not self.i2c.try_lock():
            pass
        time.sleep(0.1)
        self.i2c.unlock()
        self.mcp = MCP23017(self.i2c, address=address)

        # Configure all 16 pins (0–15) as inputs
        self.pins = [self.mcp.get_pin(i) for i in range(16)]
        for pin in self.pins:
            pin.direction = Direction.INPUT

    def read_pin(self, pin_number):
        """Read individual input pin 0–15."""
        if not 0 <= pin_number <= 15:
            raise ValueError("pin_number must be in 0–15")
        return self.pins[pin_number].value

    def read_all(self):
        """Return all 16 input bits as a single integer (bitmask)."""
        return sum((pin.value << i) for i, pin in enumerate(self.pins))
