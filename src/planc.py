import serial
import struct

ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=2)

labels = [
    "PM1.0_CF1", "PM2.5_CF1", "PM10_CF1",
    "PM1.0_ATM", "PM2.5_ATM", "PM10_ATM",
    "0.3–0.5um", "0.5–1.0um", "1.0–2.5um",
    "2.5–5.0um", "5.0–10um", ">10um"
]

def read_pms1003():
    while True:
        if ser.read(1) == b'\x42':
            if ser.read(1) == b'\x4d':
                frame = ser.read(30)
                if len(frame) != 30:
                    continue

                data = struct.unpack('!HHHHHHHHHHHHHH', frame[:28])
                checksum = struct.unpack('!H', frame[28:30])[0]
                calc_checksum = 0x42 + 0x4D + sum(frame[:28])
                if checksum == (calc_checksum & 0xFFFF):
                    return data[:12]

# Print column headers once
print(' '.join(labels))

try:
    while True:
        data = read_pms1003()
        print(' '.join(str(x) for x in data))
except KeyboardInterrupt:
    print("\nStopped")
finally:
    ser.close()
