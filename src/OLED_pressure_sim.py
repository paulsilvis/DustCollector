import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw

# OLED setup
i2c = busio.I2C(board.SCL, board.SDA)
WIDTH, HEIGHT = 128, 64
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Clear display
oled.fill(0)
oled.show()

# Frame buffer for pressure values
pressure_data = [HEIGHT // 2] * WIDTH

# Simulated pressure value and state machine
pressure = 0.0
timestep = 0

def simulate_pressure(t):
    global pressure
    if t < 20:
        pressure += 5.0
    elif t < 50:
        pass
    elif t < 150:
        pressure -= 1.0
    else:
        pressure = 0
        t = 0
    pressure = max(0, min(100, pressure))
    return t + 1

def map_pressure_to_y(p):
    return int((1.0 - (p / 100.0)) * (HEIGHT - 1))

def update_buffer(y):
    pressure_data.pop(0)
    pressure_data.append(y)

def draw_plot():
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    for x in range(1, WIDTH):
        draw.line(
            [(x - 1, pressure_data[x - 1]), (x, pressure_data[x])],
            fill=255
        )
    oled.image(image)
    oled.show()

# Main loop
while True:
    timestep = simulate_pressure(timestep)
    y = map_pressure_to_y(pressure)
    update_buffer(y)
    draw_plot()
    time.sleep(0.1)  # ~10 Hz update
