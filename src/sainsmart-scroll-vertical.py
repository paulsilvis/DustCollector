from RPLCD.i2c import CharLCD
import time

lcd = CharLCD('PCF8574', 0x3f, cols=20, rows=4)
lcd.backlight_enabled = True

# Your "tall" message as a list of strings
content = [
    "Line 1: Welcome,",
    "Line 2: This is Paul",
    "Line 3: Testing LCD",
    "Line 4: Fake scroll!",
    "Line 5: Look at this",
    "Line 6: Still scrolling",
    "Line 7: Almost there",
    "Line 8: End of demo!"
]

def display_window(start_line):
    lcd.clear()
    for i in range(4):
        if start_line + i < len(content):
            lcd.cursor_pos = (i, 0)
            lcd.write_string(content[start_line + i].ljust(20))

try:
    for pos in range(len(content) - 3):
        display_window(pos)
        time.sleep(1)

    lcd.cursor_pos = (3, 0)
    lcd.write_string("  --THE END--      ")
    time.sleep(2)
#    lcd.clear()
finally:
    lcd.backlight_enabled = False
