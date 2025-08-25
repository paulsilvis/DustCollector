import serial
import RPi.GPIO as GPIO
import time

SERIAL_PORT = "/dev/ttyS0"
BAUDRATE = 9600
GPIO_PIN = 24

THRESHOLD = 35
HYSTERESIS = 5
ALPHA = 0.1  # smoothing factor for EMA

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)
GPIO.output(GPIO_PIN, GPIO.LOW)

def find_frame(ser):
    """Scan until a valid frame header (0x42 0x4D) and read full frame."""
    while True:
        b1 = ser.read(1)
        if b1 != b'\x42':
            continue
        b2 = ser.read(1)
        if b2 != b'\x4D':
            continue
        rest = ser.read(30)
        if len(rest) != 30:
            continue
        frame = b1 + b2 + rest
        if verify_checksum(frame):
            return frame
        else:
            print("✖ Checksum failed. Resyncing...")

def verify_checksum(frame):
    """Return True if checksum is valid."""
    if len(frame) != 32:
        return False
    data = frame[:30]
    checksum_bytes = frame[30:]
    expected = int.from_bytes(checksum_bytes, byteorder='big')
    actual = sum(data)
    return actual == expected

def parse_pm2_5(frame):
    """Extract PM2.5 (standard atmosphere) from frame."""
    return (frame[6] << 8) | frame[7]

def main():
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=2)
    ser.reset_input_buffer()

    blower_on = False
    filtered = None

    try:
        while True:
            frame = find_frame(ser)
            raw = parse_pm2_5(frame)

            if filtered is None:
                filtered = raw
            else:
                filtered = ALPHA * raw + (1 - ALPHA) * filtered

            print(f"PM2.5 raw: {raw:.1f}  →  filtered: {filtered:.1f} µg/m³")

            if not blower_on and filtered >= THRESHOLD:
                print("→ Air dirty. Turning ON GPIO 24")
                GPIO.output(GPIO_PIN, GPIO.HIGH)
                blower_on = True
            elif blower_on and filtered < (THRESHOLD - HYSTERESIS):
                print("→ Air clean. Turning OFF GPIO 24")
                GPIO.output(GPIO_PIN, GPIO.LOW)
                blower_on = False

            time.sleep(0.8)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        GPIO.output(GPIO_PIN, GPIO.LOW)
        GPIO.cleanup()
        ser.close()

if __name__ == "__main__":
    main()
