import time
import os

def get_cpu_temperature():
    """Read the CPU temperature in Celsius."""
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp_milli_c = int(f.read().strip())
    return temp_milli_c / 1000.0

def plot_temperature(temp, max_temp=80):
    """Plot temperature using '*' characters."""
    stars = '*' * int(temp)
    print(f"{temp:5.1f}°C | {stars}")

def clear_screen():
    """Clear the terminal screen."""
    os.system("clear")

def main():
    print("Raspberry Pi CPU Temperature Monitor (Press Ctrl+C to stop)")
    try:
        while True:
            temp = get_cpu_temperature()
            plot_temperature(temp)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
