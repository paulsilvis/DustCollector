import time
import numpy as np
from PIL import Image, ImageDraw
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306

# --- Display Setup ---
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=64)

# --- Parameters ---
WIDTH = 128
HEIGHT = 64
N_FRAMES = 9
FRAME_DELAY = 0.1
TOP_LABEL_HEIGHT = 10
MARGIN = 6  # Margin below label and above bottom

# --- Generate X-axis (0 to 2π across screen width) ---
x = np.linspace(0, 2 * np.pi, WIDTH)

# --- Precompute partial sums for square wave ---
frames = []
for k in range(1, 2 * N_FRAMES, 2):  # odd harmonics: 1, 3, 5, ...
    partial = np.zeros_like(x)
    for n in range(1, k + 1, 2):
        partial += np.sin(n * x) / n
    wave = (4 / np.pi) * partial
    drawable_height = HEIGHT - TOP_LABEL_HEIGHT
    amplitude = (drawable_height // 2) - MARGIN
    y_vals = TOP_LABEL_HEIGHT + drawable_height // 2 - (wave * amplitude).astype(int)
    frames.append(y_vals)

# --- Image buffer ---
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# --- Animation Loop (no full clear) ---
last_frame = None

while True:
    for idx, frame in enumerate(frames):
        # Erase only previous waveform
        if last_frame is not None:
            for i in range(WIDTH - 1):
                draw.line((i, last_frame[i], i + 1, last_frame[i + 1]), fill=0)

        # Draw new waveform
        for i in range(WIDTH - 1):
            draw.line((i, frame[i], i + 1, frame[i + 1]), fill=255)

        # Add label at top
        draw.rectangle((0, 0, WIDTH, TOP_LABEL_HEIGHT), fill=0)  # clear label area
        draw.text((0, 0), f"iteration: {idx + 1}", fill=255)

        device.display(image)
        last_frame = frame
        time.sleep(FRAME_DELAY)
