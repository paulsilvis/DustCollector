# motor1_limit_sweep.py
# Drive Motor 1 between OPEN(34) and CLOSED(33) limit switches via PCF8574.
# - OPEN and CLOSED are active-low (0 when asserted).
# - Direction convention: cw = 0, ccw = 1.
# - Step cadence ~50 steps/second.
#
# Depends on:
#   - distributor.Distributor (your existing motor driver)
#   - pcf8574_in.PCF8574_in (your existing input expander wrapper)

from __future__ import annotations

import atexit
import time
from typing import Tuple

import RPi.GPIO as GPIO  # noqa: F401  (Distributor likely uses GPIO)
from distributor import Distributor
from pcf8574_in import PCF8574_in

# ----------------------------- CONFIG -------------------------------- #

MOTOR_ID = 1

PIN_OPEN = 34      # flat index: 32..39 live on device at 0x24
PIN_CLOSED = 33

# Direction bits for Distributor.set_dir(motor, dir_bit)
DIR_CW = 0
DIR_CCW = 1

# ~50 steps/second -> 20 ms period between step pulses
STEP_INTERVAL_S = 0.02

# Small confirmation to avoid reacting to bounce (ms)
CONFIRM_MS = 10

# Addresses 0x20..0x24 provide 40 inputs total
_DEV = [PCF8574_in(address=0x20 + i) for i in range(5)]


# ----------------------------- INPUTS -------------------------------- #

def _pack_40(b0: int, b1: int, b2: int, b3: int, b4: int) -> int:
    return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24) | (b4 << 32)


def _read_all_flat() -> int:
    # Keep the exact semantics of your pcf8574_test.py
    b = [dev.read_all() & 0xFF for dev in _DEV]
    return _pack_40(*b)


def _limits_low() -> Tuple[bool, bool]:
    """Return (open_low, closed_low), True if the switch is asserted."""
    val = _read_all_flat()
    open_low = ((val >> PIN_OPEN) & 1) == 0
    closed_low = ((val >> PIN_CLOSED) & 1) == 0
    return open_low, closed_low


def _confirmed_low(pin_idx: int) -> bool:
    """Return True if a given flat pin remains LOW for CONFIRM_MS."""
    t0 = time.monotonic()
    while (time.monotonic() - t0) * 1000 < CONFIRM_MS:
        val = _read_all_flat()
        if ((val >> pin_idx) & 1) != 0:
            return False
        time.sleep(0.001)
    return True


# ----------------------------- MOTOR --------------------------------- #

def _stop_motor(dist: Distributor) -> None:
    # For a step/dir driver the "stop" is simply not issuing further steps.
    # Optionally you can disable the driver coil current:
    dist.set_enable(MOTOR_ID, False)


def _start_motor(dist: Distributor) -> None:
    dist.set_enable(MOTOR_ID, True)


def _set_dir(dist: Distributor, dir_bit: int) -> None:
    dist.set_dir(MOTOR_ID, dir_bit)


def _step_once(dist: Distributor) -> None:
    dist.step(MOTOR_ID)
    time.sleep(STEP_INTERVAL_S)


# ------------------------------ MAIN --------------------------------- #

def main() -> None:
    dist = Distributor()
    atexit.register(dist.close)
    dist.reset()

    # Enable only Motor 1
    dist.set_enable(MOTOR_ID, True)

    print(
        "Motor 1 limit-sweep running @ ~50 sps (cw=0, ccw=1). "
        "Limits: OPEN=34 (LOW=hit), CLOSED=33 (LOW=hit)."
    )

    # Start from "middle": choose CW first
    direction = DIR_CW
    _set_dir(dist, direction)
    _start_motor(dist)

    last_hit = None  # None, 33, or 34

    try:
        while True:
            # Take one step, then check limits
            _step_once(dist)
            open_low, closed_low = _limits_low()

            # Safety: both asserted -> stop & exit
            if open_low and closed_low:
                print("Both 33 and 34 are LOW! Stopping for safety.")
                _stop_motor(dist)
                break

            if last_hit is None:
                # First leg: stop at whichever limit we encounter first
                if open_low and _confirmed_low(PIN_OPEN):
                    print("Hit 34 (OPEN). Reversing.")
                    last_hit = 34
                    _stop_motor(dist)
                    direction = DIR_CCW
                    _set_dir(dist, direction)
                    _start_motor(dist)
                    continue

                if closed_low and _confirmed_low(PIN_CLOSED):
                    print("Hit 33 (CLOSED). Reversing.")
                    last_hit = 33
                    _stop_motor(dist)
                    direction = DIR_CCW
                    _set_dir(dist, direction)
                    _start_motor(dist)
                    continue

                continue  # keep moving until first limit

            # After first hit: seek the *other* limit
            if last_hit == 34 and closed_low and _confirmed_low(PIN_CLOSED):
                print("Hit 33 (CLOSED). Reversing.")
                last_hit = 33
                _stop_motor(dist)
                direction = DIR_CW
                _set_dir(dist, direction)
                _start_motor(dist)
                continue

            if last_hit == 33 and open_low and _confirmed_low(PIN_OPEN):
                print("Hit 34 (OPEN). Reversing.")
                last_hit = 34
                _stop_motor(dist)
                direction = DIR_CCW
                _set_dir(dist, direction)
                _start_motor(dist)
                continue

    except KeyboardInterrupt:
        print("\nInterrupted. Stopping motor.")
    finally:
        _stop_motor(dist)
        # If you want all motors disabled explicitly:
        for m in (1, 2, 3, 4):
            try:
                dist.set_enable(m, False)
            except Exception:
                pass
        print("Stopped. Driver(s) disabled.")


if __name__ == "__main__":
    main()
