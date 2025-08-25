from RPLCD.i2c import CharLCD
import time

# Adjust address if necessary (0x27 or 0x3F are common)
lcd = CharLCD('PCF8574', 0x3f, cols=20, rows=4)

lcd.backlight_enabled = True

# Write to each line
lcd.cursor_pos = (0, 0)
lcd.write_string("Hello, Gary!")

lcd.cursor_pos = (1, 0)
lcd.write_string("All Systems Go!")
lcd.cursor_pos = (2, 0)
lcd.write_string("Welcome to Boston!")
lcd.cursor_pos = (3, 0)
lcd.write_string("Go get me a beer!")

while True:
	time.sleep(1)
