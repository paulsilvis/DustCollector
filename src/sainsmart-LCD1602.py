from RPLCD.i2c import CharLCD
from time import sleep

# Adjust address and port_expander if needed (common values below)
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
              cols=16, rows=2, charmap='A00', auto_linebreaks=True)

lcd.clear()
lcd.write_string("Hello, Paul!")
sleep(2)
lcd.cursor_pos = (1, 0)
lcd.write_string("All Systems GOOD")
