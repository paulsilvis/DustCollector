from RPLCD.i2c import CharLCD
import time

# Adjust address if necessary (0x27 or 0x3F are common)
lcd = CharLCD('PCF8574', 0x3f, cols=20, rows=4)

lcd.backlight_enabled = True

# Write to each line
lcd.cursor_pos = (0, 0)
lcd.write_string("Hello, Paul!")

lcd.cursor_pos = (1, 0)
lcd.write_string("Sainsmart LCD2004")

lcd.cursor_pos = (2, 0)
lcd.write_string("Python + I2C demo")

lcd.cursor_pos = (3, 0)
lcd.write_string("Scrolling starts...")

time.sleep(2)

# Scroll to the left
for i in range(20):
    lcd.shift_display(-1)
    time.sleep(0.3)

lcd.clear()
lcd.write_string("Done scrolling!")
time.sleep(1000)

lcd.backlight_enabled = False
