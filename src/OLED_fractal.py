import time
import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw

# Init I2C and display
i2c = busio.I2C(board.SCL, board.SDA)
WIDTH = 128
HEIGHT = 64
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Create blank image buffer
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# Clear display
oled.fill(0)
oled.show()

# Mandelbrot parameters
max_iter = 20
zoom = 1.0
offset_x = -0.5
offset_y = 0.0

def mandelbrot(x, y):
    zx, zy = 0, 0
    cx, cy = x, y
    for i in range(max_iter):
        zx2, zy2 = zx*zx, zy*zy
        if zx2 + zy2 > 4:
            return i
        zy = 2*zx*zy + cy
        zx = zx2 - zy2 + cx
    return max_iter

# Generate Mandelbrot image
for px in range(WIDTH):
    for py in range(HEIGHT):
        # Map pixel to complex plane
        x = (px - WIDTH / 2) / (0.5 * zoom * WIDTH) + offset_x
        y = (py - HEIGHT / 2) / (0.5 * zoom * HEIGHT) + offset_y
        color = mandelbrot(x, y)
        if color < max_iter:
            draw.point((px, py), fill=255)

# Display it
oled.image(image)
oled.show()
