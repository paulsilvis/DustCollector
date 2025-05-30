import time
from pcf8574_in import PCF8574_in
from RPLCD.i2c import CharLCD

def bits_to_str(val):
    return "".join("1" if (val >> i) & 1 else "0" for i in reversed(range(8)))

def main():

#    lcd = CharLCD('PCF8574', address=0x27, port=1, cols=16, rows=2)
    dev0 = PCF8574_in(address=0x20)
    dev1 = PCF8574_in(address=0x21)
    dev2 = PCF8574_in(address=0x22)
    dev3 = PCF8574_in(address=0x23)
    dev4 = PCF8574_in(address=0x24)

    while True:
        value = dev0.read_all()

        b0 = dev0.read_all()
        b1 = dev1.read_all()
        #bit_str = bits_to_str(b1) + bits_to_str(b0)
        #lcd.cursor_pos = (0, 0)
        #lcd.write_string(bit_str)

        b2 = dev2.read_all()
        b3 = dev3.read_all()
        #bit_str = bits_to_str(b3) + bits_to_str(b2)
        #lcd.cursor_pos = (1, 0)
        #lcd.write_string(bit_str)

        b4 = dev4.read_all()
#        print(bin(b0), bin(b1), bin(b2), bin(b3), bin(b4))
#        active = [str(i) for i in range(8) if not ((value >> i) & 1)]
        value = b0 + (b1<<8) + (b2<<16) + (b3<<24) + (b4<<32)
        active = [str(i) for i in range(40) if not ((value>>i) & 1)]
        if active:
            print("Pins LOW (pressed):", ", ".join(active))
        else:
            print("No buttons pressed.")
        time.sleep(0.2)

if __name__ == "__main__":
    main()
