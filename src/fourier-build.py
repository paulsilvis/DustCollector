from math import sin, pi
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from time import sleep

# Display parameters
WIDTH, HEIGHT = 128, 64
NUM_HARMONICS = 14
SWEEP_DELAY = 0.001  # seconds between pixel columns

# Setup OLED
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=WIDTH, height=HEIGHT)
font = ImageFont.load_default()

# Center and amplitude
y_center = HEIGHT // 2 + 8
amplitude = HEIGHT // 3

# X values for sine computation
x_vals = [2 * pi * x / WIDTH for x in range(WIDTH)]

# Initialize previous sum to zero
prev_sum = [0.0] * WIDTH

# Clear screen initially
device.clear()

for n_index, n in enumerate(range(1, NUM_HARMONICS * 2, 2), start=1):
    # Compute current harmonic
    harmonic = [sin(n * x) / n for x in x_vals]

    # Animate sweep
    #for sweep_x in range(WIDTH + 1):
    for sweep_x in range(0, WIDTH + 1, 4):  # Step by 2 pixels
        img = Image.new("1", (WIDTH, HEIGHT), 0)
        draw = ImageDraw.Draw(img)

        # Label
        label = f"+ sin({n}x)/{n}"
        draw.text((2, 0), label, font=font, fill=1)

        # Optional: draw current harmonic (light wave)
        for x in range(WIDTH - 1):
            y1 = int(y_center + amplitude * -harmonic[x])
            y2 = int(y_center + amplitude * -harmonic[x + 1])
            draw.line((x, y1, x + 1, y2), fill=1)

        # Draw sum so far with current harmonic added up to sweep_x
        current_sum = [
            prev_sum[x] + (harmonic[x] if x < sweep_x else 0.0)
            for x in range(WIDTH)
        ]

        for x in range(WIDTH - 1):
            y1 = int(y_center + amplitude * -current_sum[x])
            y2 = int(y_center + amplitude * -current_sum[x + 1])
            draw.line((x, y1, x + 1, y2), fill=1)

        # Display the frame
        device.display(img)
        #sleep(SWEEP_DELAY)

    # Finalize sum
    prev_sum = [prev_sum[x] + harmonic[x] for x in range(WIDTH)]
