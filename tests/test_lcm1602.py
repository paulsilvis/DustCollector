from RPLCD.i2c import CharLCD
from time import sleep, strftime
from datetime import datetime

# Create LCD object using the default I2C address (often 0x27 or 0x3F)
lcd = CharLCD('PCF8574', 0x27)

try:
    lcd.clear()
    lcd.write_string("Hello, world!")
    sleep(2)

    while True:
        lcd.cursor_pos = (1, 0)
        lcd.write_string(strftime('%H:%M:%S  '))
        sleep(1)

except KeyboardInterrupt:
    pass
finally:
    lcd.clear()
