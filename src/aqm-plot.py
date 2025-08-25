import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from datetime import datetime

# -----------------------------
# Configuration
# -----------------------------
SERIAL_PORT = "/dev/ttyS0"
BAUDRATE = 9600
ALPHA = 0.1  # EMA smoothing factor
UPDATE_INTERVAL = 5000  # milliseconds
WINDOW_SECONDS = 300  # plot 5 minutes of data
MAX_POINTS = WINDOW_SECONDS // (UPDATE_INTERVAL // 1000)

# -----------------------------
# Data Buffers
# -----------------------------
timestamps = deque(maxlen=MAX_POINTS)
raw_vals = deque(maxlen=MAX_POINTS)
ema_vals = deque(maxlen=MAX_POINTS)
ema = None

# -----------------------------
# Serial Reader
# -----------------------------
def read_pm2_5_from_sensor(ser):
    while True:
        if ser.read() == b'\x42':
            if ser.read() == b'\x4d':
                frame = ser.read(30)
                data = list(frame)
                pm2_5_atm = data[8] << 8 | data[9]  # Correct offset
                return pm2_5_atm

# -----------------------------
# Plot Setup
# -----------------------------
fig, ax = plt.subplots(figsize=(7, 3))
line_raw, = ax.plot([], [], label="Raw PM2.5", color="gray")
line_ema, = ax.plot([], [], label="EMA", linewidth=2, color="blue")
ax.axhline(35, color="red", linestyle="--", label="Threshold")
ax.set_xlabel("Time")
ax.set_ylabel("µg/m³")
ax.set_title("PM2.5 (ATM) — Real-Time")
ax.legend()
ax.grid(True)

# -----------------------------
# Update Function
# -----------------------------
def update(frame):
    global ema

    pm = read_pm2_5_from_sensor(ser)

    if ema is None:
        ema = pm
    else:
        ema = ALPHA * pm + (1 - ALPHA) * ema

    now = datetime.now().strftime("%H:%M:%S")
    timestamps.append(now)
    raw_vals.append(pm)
    ema_vals.append(ema)

    line_raw.set_data(timestamps, raw_vals)
    line_ema.set_data(timestamps, ema_vals)

    ax.set_xlim(timestamps[0], timestamps[-1])
    ax.set_ylim(0, max(max(raw_vals), max(ema_vals), 50) + 10)

    return line_raw, line_ema

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=2)

    ani = animation.FuncAnimation(
        fig,
        update,
        interval=UPDATE_INTERVAL,
        cache_frame_data=False
    )

    plt.tight_layout()
    print("Starting animation ...")
    plt.show()
