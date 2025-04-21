from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image

# Setup I2C interface and OLED device
serial = i2c(port=1, address=0x3C)  # Check with i2cdetect if needed
device = ssd1306(serial)

# Clear the screen
device.clear()

# Load the 128x64 1-bit image of Harper (must be in same folder)
image = Image.open("harper_bw.png").convert("1")

# Display it on the OLED
device.display(image)
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image
import time

# Initialize I2C interface and OLED device
serial = i2c(port=1, address=0x3C)  # Use 'i2cdetect -y 1' to confirm address
device = ssd1306(serial)

# Clear screen first
device.clear()

# Load and convert the preprocessed image
image = Image.open("harper_bw.png").convert("1")

# Optional: Fade-in effect
for step in range(1, 11):
    brightness = step / 10.0
    faded = image.convert("L").point(lambda x: x * brightness)
    device.display(faded.convert("1"))
    time.sleep(0.1)

# Show the final image
device.display(image)

while True:
	pass
