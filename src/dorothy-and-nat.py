
import atexit
from RPLCD.i2c import CharLCD
import time

def backlight_off():
    lcd.backlight_enabled = False

atexit.register(lambda : backlight_off)

# Adjust address if necessary (0x27 or 0x3F are common)
lcd = CharLCD('PCF8574', 0x3f, cols=20, rows=4)

lcd.backlight_enabled = True

# Write to each line
lcd.cursor_pos = (0, 0)
lcd.write_string("Hello, Dorothy!")

lcd.cursor_pos = (1, 0)
lcd.write_string("Hello, Natalie!")

lcd.cursor_pos = (2, 0)
lcd.write_string("Hello, Derek!")

lcd.cursor_pos = (3, 0)
lcd.write_string("Hello, Harper!")

time.sleep(100000)

lcd.backlight_enabled = False
