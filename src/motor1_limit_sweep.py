# motor1_open_close_cli.py
# Interactive gate control for Motor 1 using PCF8574 inputs.
# - Prompt: "open or close?" and act accordingly.
# - OPEN  = flat pin 34 (active-low)
# - CLOSED= flat pin 33 (active-low)
# - cw = 0, ccw = 1
# - ~50 steps/second
#
# Depends on:
#   - distributor.Distributor
#   - pcf8574_in.PCF8574_in

from __future__ import annotations

import atexit
import time
from typing import Tuple

import RPi.GPIO as GPIO  # noqa: F401  (Distributor may use GPIO)
from distributor import Distributor
from pcf8574_in import PCF8574_in

# -------------------------- CONFIG ----------------------------------- #

MOTOR_ID = 1

PIN_OPEN = 34
PIN_CLOSED = 33

DIR_CW = 0
DIR_CCW = 1

STEP_INTERVAL_S = 0.02       # 50 steps/s
DIR_SETUP_S = 0.0005         # small dir->step setup pause

_DEVS = [PCF8574_in(address=0x20 + i) for i in range(5)]


# -------------------------- INPUTS ----------------------------------- #

def _pack_40(b0: int, b1: int, b2: int, b3: int, b4: int) -> int:
    return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24) | (b4 << 32)


def _read_all_flat() -> int:
    b = [dev.read_all() & 0xFF for dev in _DEVS]
    return _pack_40(*b)


def _limits_low() -> Tuple[bool, bool]:
    """Return (open_low, closed_low)."""
    val = _read_all_flat()
    return ((val >> PIN_OPEN) & 1) == 0, ((val >> PIN_CLOSED) & 1) == 0


# -------------------------- MOTOR ------------------------------------ #

def _set_dir(dist: Distributor, dir_bit: int) -> None:
    dist.set_dir(MOTOR_ID, dir_bit)


def _step(dist: Distributor) -> None:
    dist.step(MOTOR_ID)


# -------------------------- ACTIONS ---------------------------------- #

def _move_until_open(dist: Distributor) -> None:
    """Run CW until OPEN (pin 34) goes LOW; then stop."""
    _set_dir(dist, DIR_CW)
    time.sleep(DIR_SETUP_S)

    # Already open?
    open_low, closed_low = _limits_low()
    if open_low:
        print("Already OPEN (pin 34 LOW).")
        return

    print("Opening... (cw=0) -> waiting for pin 34 LOW")
    while True:
        open_low, closed_low = _limits_low()

        if open_low:
            print("Reached OPEN (pin 34 LOW). Stopping.")
            return

        if open_low and closed_low:
            print("Both pins LOW! Safety stop.")
            return

        _step(dist)
        time.sleep(STEP_INTERVAL_S)


def _move_until_closed(dist: Distributor) -> None:
    """Run CCW until CLOSED (pin 33) goes LOW; then stop."""
    _set_dir(dist, DIR_CCW)
    time.sleep(DIR_SETUP_S)

    # Already closed?
    open_low, closed_low = _limits_low()
    if closed_low:
        print("Already CLOSED (pin 33 LOW).")
        return

    print("Closing... (ccw=1) -> waiting for pin 33 LOW")
    while True:
        open_low, closed_low = _limits_low()

        if closed_low:
            print("Reached CLOSED (pin 33 LOW). Stopping.")
            return

        if open_low and closed_low:
            print("Both pins LOW! Safety stop.")
            return

        _step(dist)
        time.sleep(STEP_INTERVAL_S)


# -------------------------- MAIN LOOP -------------------------------- #

def _prompt_open_or_close() -> str:
    while True:
        cmd = input("open or close? ").strip().lower()
        if cmd in ("open", "o"):
            return "open"
        if cmd in ("close", "c"):
            return "close"
        print('Please type "open" or "close".')


def main() -> None:
    dist = Distributor()
    atexit.register(dist.close)
    dist.reset()

    # Hold torque for Motor 1 through the loop
    dist.set_enable(MOTOR_ID, True)

    print(
        "Interactive Motor 1 control @ ~50 sps (cw=0, ccw=1).\n"
        "Limits: OPEN=34 LOW, CLOSED=33 LOW.\n"
    )

    try:
        while True:
            choice = _prompt_open_or_close()
            if choice == "open":
                _move_until_open(dist)
            else:
                _move_until_closed(dist)
            # Loop back to the prompt to simulate tool on/off cycles
    except KeyboardInterrupt:
        print("\nInterrupted. Stopping.")
    finally:
        # Disable all motors on exit
        try:
            dist.set_enable(MOTOR_ID, False)
            for m in (2, 3, 4):
                dist.set_enable(m, False)
        except Exception:
            pass
        print("Stopped. Drivers disabled.")


if __name__ == "__main__":
    main()
