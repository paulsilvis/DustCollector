import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# OLED setup
i2c = busio.I2C(board.SCL, board.SDA)
WIDTH, HEIGHT = 128, 64
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Clear display
oled.fill(0)
oled.show()

# Fonts
font = ImageFont.load_default()

# Pressure plot data
pressure_data = [HEIGHT // 2] * WIDTH
pressure = 0.0
timestep = 0

# Gate position data
gate_steps = 0
gate_max_steps = 200

# Mode toggle
mode = 0  # 0 = Pressure, 1 = Gate
mode_time = time.monotonic()

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

def simulate_gate():
    global gate_steps
    gate_steps += 5
    if gate_steps > gate_max_steps:
        gate_steps = 0

def map_pressure_to_y(p):
    return int((1.0 - (p / 100.0)) * (HEIGHT - 1))

def update_pressure_buffer(y):
    pressure_data.pop(0)
    pressure_data.append(y)

def draw_pressure_plot():
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    for x in range(1, WIDTH):
        draw.line(
            [(x - 1, pressure_data[x - 1]), (x, pressure_data[x])],
            fill=255
        )
    draw.text((0, 0), "Pressure", font=font, fill=255)
    oled.image(image)
    oled.show()

def draw_gate_position():
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    # Calculate bar height
    bar_h = int((gate_steps / gate_max_steps) * 40)
    bar_y = 20 + (40 - bar_h)

    draw.text((0, 0), "Gate Position", font=font, fill=255)
    draw.rectangle((100, 0, 127, 15), outline=255)
    draw.text((102, 2), f"{gate_steps}", font=font, fill=255)

    draw.rectangle((50, 20, 70, 60), outline=255)
    draw.rectangle((50, bar_y, 70, bar_y + bar_h), fill=255)

    oled.image(image)
    oled.show()

# Main loop
while True:
    now = time.monotonic()
    if now - mode_time > 10:
        mode = (mode + 1) % 2
        mode_time = now

    if mode == 0:
        timestep = simulate_pressure(timestep)
        y = map_pressure_to_y(pressure)
        update_pressure_buffer(y)
        draw_pressure_plot()
    else:
        simulate_gate()
        draw_gate_position()

    time.sleep(0.1)
