import time
import os

def get_cpu_temp_fahrenheit():
    """Reads Pi CPU temp in Fahrenheit."""
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp_str = f.readline().strip()
    temp_c = float(temp_str) / 1000.0
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_f

while True:
    
        # Read CPU temp
        temp_f = get_cpu_temp_fahrenheit()
        temp_f = get_cpu_temp_fahrenheit()
        bar_length = int(temp_f / 2)
        bar = " " + "█" * bar_length
        print(f"CPU Temperature: {temp_f:.2f} °F{bar}")

        time.sleep(1.0)

