import serial
import struct

# Open serial port
ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=2)

def read_pms1003():
    while True:
        byte = ser.read(1)
        if byte == b'\x42':
            second = ser.read(1)
            if second == b'\x4d':
                frame = ser.read(30)
                data = struct.unpack('!HHHHHHHHHHHHHH', frame[:28])
                pm1_cf1 = data[0]
                pm25_cf1 = data[1]
                pm10_cf1 = data[2]
                pm1_atm = data[3]
                pm25_atm = data[4]
                pm10_atm = data[5]
                checksum = struct.unpack('!H', frame[28:30])[0]
                calculated_checksum = 0x42 + 0x4D + sum(frame[:28])
                if checksum == (calculated_checksum & 0xFFFF):
                    return {
                        "PM1.0": pm1_atm,
                        "PM2.5": pm25_atm,
                        "PM10": pm10_atm
                    }

while True:
    data = read_pms1003()
    print("PM2.5:", data['PM2.5'], "μg/m³")
