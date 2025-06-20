import asyncio
import time
from collections import defaultdict

N_ITERATIONS = 500  # Total number of task iterations

# Simulated durations (in seconds)
TASK_DELAYS = {
    'motor': 0.0005,        # 0.5 ms
    'current': 0.001,       # 1.0 ms
    'limit': 0.0002,        # 0.2 ms
    'lcd': 0.002,           # 2.0 ms
    'display': 0.003        # 3.0 ms
}

async def motor_task(stats):
    for _ in range(N_ITERATIONS):
        t0 = time.perf_counter()
        await asyncio.sleep(TASK_DELAYS['motor'])
        stats['motor'].append(time.perf_counter() - t0)

async def current_task(stats):
    for _ in range(N_ITERATIONS):
        t0 = time.perf_counter()
        await asyncio.sleep(TASK_DELAYS['current'])
        stats['current'].append(time.perf_counter() - t0)

async def limit_switch_task(stats):
    for _ in range(N_ITERATIONS):
        t0 = time.perf_counter()
        await asyncio.sleep(TASK_DELAYS['limit'])
        stats['limit'].append(time.perf_counter() - t0)

async def lcd_task(stats):
    for _ in range(N_ITERATIONS):
        t0 = time.perf_counter()
        await asyncio.sleep(TASK_DELAYS['lcd'])
        stats['lcd'].append(time.perf_counter() - t0)

async def display_task(stats):
    for _ in range(N_ITERATIONS):
        t0 = time.perf_counter()
        await asyncio.sleep(TASK_DELAYS['display'])
        stats['display'].append(time.perf_counter() - t0)

async def main():
    stats = defaultdict(list)

    print(f"Running {N_ITERATIONS} iterations per task...\n")
    start_time = time.perf_counter()

    await asyncio.gather(
        motor_task(stats),
        current_task(stats),
        limit_switch_task(stats),
        lcd_task(stats),
        display_task(stats),
    )

    total_time = time.perf_counter() - start_time
    print(f"Total run time: {total_time:.3f} sec\n")

    for name, durations in stats.items():
        avg = sum(durations) / len(durations)
        max_t = max(durations)
        min_t = min(durations)
        print(f"{name:<10}: avg={avg*1e3:.3f} ms  max={max_t*1e3:.3f} ms  min={min_t*1e3:.3f} ms")

if __name__ == "__main__":
    asyncio.run(main())
