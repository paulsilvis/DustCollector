# motor1_tablesaw_autogate.py
# Motor 1 auto gate control driven by tablesaw current on ADS1115 CH0.
# - OPEN  limit = flat pin 34 (LOW == asserted)
# - CLOSED limit = flat pin 33 (LOW == asserted)
# - Direction convention: cw = 0, ccw = 1
# - No holding torque: driver enabled only while stepping
# - ~50 steps/s
#
# Depends on:
#   - distributor.Distributor
#   - pcf8574_in.PCF8574_in
#   - Adafruit ADS1x15 (CircuitPython): board, busio, adafruit_ads1x15

from __future__ import annotations

import atexit
import time
from typing import Tuple

import RPi.GPIO as GPIO  # noqa: F401
from distributor import Distributor
from pcf8574_in import PCF8574_in

import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# -------------------------- CONFIG ----------------------------------- #

MOTOR_ID = 1

PIN_OPEN = 34
PIN_CLOSED = 33

DIR_CW = 0
DIR_CCW = 1

# Step timing (~50 steps/s)
STEP_INTERVAL_S = 0.0025
DIR_SETUP_S = 0.0005  # small dir->step setup pause

# ADS1115 thresholds (volts) with hysteresis; tune for your sensor
SAW_ON_THRESH_V = 0.50   # >= this -> saw considered ON
SAW_OFF_THRESH_V = 0.30  # <= this -> saw considered OFF

# PCF8574 expanders at 0x20..0x24
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

def _enable(dist: Distributor, on: bool) -> None:
    dist.set_enable(MOTOR_ID, bool(on))


def _set_dir(dist: Distributor, dir_bit: int) -> None:
    dist.set_dir(MOTOR_ID, dir_bit)


def _step(dist: Distributor) -> None:
    dist.step(MOTOR_ID)


def _move_until_open(dist: Distributor) -> None:
    """Enable, run CW until OPEN (pin 34) goes LOW; then disable."""
    open_low, _ = _limits_low()
    if open_low:
        print("Already OPEN (pin 34 LOW).")
        return
    print("Opening (cw=0) until pin 34 LOW...")
    _enable(dist, True)
    _set_dir(dist, DIR_CW)
    time.sleep(DIR_SETUP_S)

    next_t = time.monotonic()
    while True:
        open_low, closed_low = _limits_low()
        if open_low:
            print("Reached OPEN (pin 34 LOW). Stopping.")
            break
        if open_low and closed_low:
            print("Both limits LOW! Safety stop.")
            break
        now = time.monotonic()
        if now < next_t:
            time.sleep(next_t - now)
        _step(dist)
        next_t += STEP_INTERVAL_S

    _enable(dist, False)


def _move_until_closed(dist: Distributor) -> None:
    """Enable, run CCW until CLOSED (pin 33) goes LOW; then disable."""
    _, closed_low = _limits_low()
    if closed_low:
        print("Already CLOSED (pin 33 LOW).")
        return
    print("Closing (ccw=1) until pin 33 LOW...")
    _enable(dist, True)
    _set_dir(dist, DIR_CCW)
    time.sleep(DIR_SETUP_S)

    next_t = time.monotonic()
    while True:
        open_low, closed_low = _limits_low()
        if closed_low:
            print("Reached CLOSED (pin 33 LOW). Stopping.")
            break
        if open_low and closed_low:
            print("Both limits LOW! Safety stop.")
            break
        now = time.monotonic()
        if now < next_t:
            time.sleep(next_t - now)
        _step(dist)
        next_t += STEP_INTERVAL_S

    _enable(dist, False)


# -------------------------- ADS1115 ---------------------------------- #

def _init_ads() -> AnalogIn:
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS1115(i2c)
    ads.gain = 1
    return AnalogIn(ads, 0)  # Channel 0 for tablesaw


def _saw_state(volts: float, was_on: bool) -> bool:
    """Hysteresis: return new saw_on state given voltage and previous."""
    if was_on:
        # stay ON until we fall below OFF threshold
        return volts > SAW_OFF_THRESH_V
    # was OFF: turn ON only when above ON threshold
    return volts >= SAW_ON_THRESH_V


# --------------------------- MAIN LOOP -------------------------------- #

def main() -> None:
    dist = Distributor()
    atexit.register(dist.close)
    dist.reset()

    # Ensure no holding torque at idle
    _enable(dist, False)

    chan0 = _init_ads()
    print(
        "Auto-gate: ADS1115 CH0 controls Motor 1 "
        "(open on ON, close on OFF).\n"
        "Limits: OPEN=34 LOW, CLOSED=33 LOW. No debounce, instant stop.\n"
        f"Hysteresis: on>={SAW_ON_THRESH_V:.3f} V, off<={SAW_OFF_THRESH_V:.3f} V."
    )

    saw_on = False
    last_print = time.monotonic()
    try:
        while True:
            v = chan0.voltage  # volts
            new_state = _saw_state(v, saw_on)

            # Edge: OFF -> ON
            if not saw_on and new_state:
                print(f"Tablesaw ON (V={v:.3f}). Opening gate.")
                _move_until_open(dist)

            # Edge: ON -> OFF
            if saw_on and not new_state:
                print(f"Tablesaw OFF (V={v:.3f}). Closing gate.")
                _move_until_closed(dist)

            saw_on = new_state

            # Occasional heartbeat
            if time.monotonic() - last_print >= 2.0:
                last_print = time.monotonic()
                state = "ON " if saw_on else "OFF"
                print(f"[hb] saw={state} V={v:.3f}")

            time.sleep(0.05)  # ~20 Hz poll
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        # Disable all motors on exit
        for m in (1, 2, 3, 4):
            try:
                dist.set_enable(m, False)
            except Exception:
                pass
        print("Stopped. Drivers disabled.")


if __name__ == "__main__":
    main()
