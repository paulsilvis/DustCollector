import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

i2c = busio.I2C(board.SCL, board.SDA)
display = SSD1306_I2C(128, 64, i2c)

# Clear the display
display.fill(0)
display.show()

# Draw text
image = Image.new("1", (display.width, display.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()
draw.text((0, 0), "Hello, Paul!", font=font, fill=255)
display.image(image)
display.show()
