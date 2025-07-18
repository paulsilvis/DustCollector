import serial
import struct
import time

ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=2)

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

try:
    while True:
        data = read_pms1003()
        print("---- PMS1003 Readings ----")

        print(f"PM1.0 (CF1): {data[0]}")
        print(f"PM2.5 (CF1): {data[1]}")
        print(f"PM10  (CF1): {data[2]}")
        print(f"PM1.0 (ATM): {data[3]}")
        print(f"PM2.5 (ATM): {data[4]}")
        print(f"PM10  (ATM): {data[5]}")
        print()

        bin_labels = [
            "0.3–0.5 μm",
            "0.5–1.0 μm",
            "1.0–2.5 μm",
            "2.5–5.0 μm",
            "5.0–10 μm",
            ">10 μm"
        ]

        for i in range(6):
            print(f"Particles {bin_labels[i]}: {data[6 + i]}")

        print()
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping...")
finally:
    ser.close()
