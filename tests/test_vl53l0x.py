import time
import VL53L0X
VL53L0X_GOOD_ACCURACY_MODE = 0
VL53L0X_BETTER_ACCURACY_MODE = 1
VL53L0X_BEST_ACCURACY_MODE = 2
VL53L0X_LONG_RANGE_MODE = 3
VL53L0X_HIGH_SPEED_MODE = 0

# Create a VL53L0X object
tof = VL53L0X.VL53L0X()
tof.open()
tof.start_ranging(VL53L0X_HIGH_SPEED_MODE)

try:
    while True:
        distance = tof.get_distance()
        #print("Distance: {} mm".format(distance))
        if distance < 300 :
            print(int((0.1*distance))*'*')
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    tof.stop_ranging()
