import asyncio
from w1thermsensor import W1ThermSensor, SensorNotReadyError


class AsyncDS18B20Reader:
    def __init__(self, retry_delay=0.5, max_retries=3):
        self.sensors = W1ThermSensor.get_available_sensors()
        self.retry_delay = retry_delay
        self.max_retries = max_retries

    async def read_temperature(self, sensor):
        for attempt in range(self.max_retries):
            try:
                temp = await asyncio.to_thread(sensor.get_temperature)
                return temp
            except SensorNotReadyError:
                await asyncio.sleep(self.retry_delay)
        return None

    async def read_all(self):
        readings = {}
        tasks = [self.read_temperature(s) for s in self.sensors]
        results = await asyncio.gather(*tasks)
        for sensor, temp in zip(self.sensors, results):
            readings[sensor.id] = temp
        return readings
