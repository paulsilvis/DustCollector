import time
import board
import busio
from smbus2 import SMBus
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

# Shared I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Constants
MUX_ADDR = 0x70
OLED_ADDR = 0x3C
NUM_DISPLAYS = 8

# Setup font
font = ImageFont.load_default()

# Setup channel selector
smbus = SMBus(1)

def select_mux_channel(channel):
    if 0 <= channel <= 7:
        smbus.write_byte(MUX_ADDR, 1 << channel)

# Initialize all OLED displays
oled_displays = []

for ch in range(NUM_DISPLAYS):
    select_mux_channel(ch)
    try:
        oled = SSD1306_I2C(128, 64, i2c, addr=OLED_ADDR)
        oled.fill(0)
        oled.show()
        oled_displays.append(oled)
    except Exception as e:
        print(f"Failed to init OLED on channel {ch}: {e}")
        oled_displays.append(None)

# Test loop: write to each display in turn
counter = 0
while True:
    for i, oled in enumerate(oled_displays):
        if oled is None:
            continue
        select_mux_channel(i)
        oled.fill(0)
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), f"Display #{i}", font=font, fill=255)
        draw.text((0, 20), f"Count: {counter}", font=font, fill=255)
        oled.image(image)
        oled.show()
    counter += 1
    time.sleep(1)
