from w1thermsensor import W1ThermSensor, SensorNotReadyError
import time

sensors = W1ThermSensor.get_available_sensors()
time.sleep(1)
print('ready')

while True:
    for s in sensors:
        for attempt in range(3):
            try:
                temp = s.get_temperature()
                print(f"{s.id}: {temp:.2f} °C")
                break
            except SensorNotReadyError:
                print(f"{s.id}: Sensor not ready (attempt {attempt+1}), retrying...")
                time.sleep(0.5)
        else:
            print(f"{s.id}: Failed to read after 3 attempts.")
    time.sleep(2)
