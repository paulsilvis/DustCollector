import asyncio
from async_temp_sensor import AsyncDS18B20Reader

async def main():
    sensor_reader = AsyncDS18B20Reader()
    print("Async sensor reader ready")

    while True:
        temps = await sensor_reader.read_all()
        for sid, temp in temps.items():
            if temp is not None:
                print(f"{sid}: {temp:.2f} °C")
            else:
                print(f"{sid}: Failed to read")
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
