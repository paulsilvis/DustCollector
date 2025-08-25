# motor1_tablesaw_autogate_leds.py
# Auto-open/close Motor 1 from ADS1115 CH0 + show state on LED PCF8574.
# - OPEN  limit (LOW) = flat pin 34
# - CLOSED limit (LOW) = flat pin 33
# - cw = 0, ccw = 1
# - No holding torque: driver enabled only while stepping
# - ~50 steps/s
# - LED PCF: bit 0 = GREEN (open), bit 4 = RED (closed)
#
# Depends on:
#   distributor.Distributor
#   pcf8574_in.PCF8574_in
#   smbus2
#   Adafruit ADS1x15 libs (board, busio, adafruit_ads1x15)

from __future__ import annotations

import atexit
import time
from typing import Tuple

import RPi.GPIO as GPIO  # noqa: F401
from smbus2 import SMBus
from distributor import Distributor
from pcf8574_in import PCF8574_in

import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# -------------------------- CONFIG ----------------------------------- #

# Motor / limits
MOTOR_ID = 1
PIN_OPEN = 34
PIN_CLOSED = 33
DIR_CW = 0
DIR_CCW = 1
STEP_INTERVAL_S = 0.0025      # 50 steps/s
DIR_SETUP_S = 0.0005        # small dir->step setup pause

# ADS thresholds (volts) — tune to your sensor
SAW_ON_THRESH_V = 0.50      # >= this -> ON
SAW_OFF_THRESH_V = 0.30     # <= this -> OFF

# LED expander (your “walking test” address)
LED_I2C_BUS = 1
LED_PCF_ADDR = 0x20         # adjust if your LED board is at another addr
LED_BIT_OPEN = 0            # GREEN
LED_BIT_CLOSED = 4          # RED

# Input expanders (5 x PCF8574)
_INPUT_DEVS = [PCF8574_in(address=0x20 + i) for i in range(5)]


# -------------------------- INPUTS ----------------------------------- #

def _pack_40(b0: int, b1: int, b2: int, b3: int, b4: int) -> int:
    return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24) | (b4 << 32)


def _read_all_flat() -> int:
    b = [dev.read_all() & 0xFF for dev in _INPUT_DEVS]
    return _pack_40(*b)


def _limits_low() -> Tuple[bool, bool]:
    """Return (open_low, closed_low)."""
    val = _read_all_flat()
    return ((val >> PIN_OPEN) & 1) == 0, ((val >> PIN_CLOSED) & 1) == 0


# -------------------------- LED OUTPUTS ------------------------------- #

_led_bus = SMBus(LED_I2C_BUS)
atexit.register(_led_bus.close)

# Start clean (as in your walking test). If you need to preserve other
# LEDs, remove this line and tell me to switch to read-modify-write only.
_led_bus.write_byte(LED_PCF_ADDR, 0x00)
_led_shadow = 0x00  # local mirror (1 = LED ON)

def _led_write() -> None:
    _led_bus.write_byte(LED_PCF_ADDR, _led_shadow & 0xFF)

def _led_on(bit: int) -> None:
    global _led_shadow
    _led_shadow |= (1 << bit)
    _led_write()

def _led_off(bit: int) -> None:
    global _led_shadow
    _led_shadow &= ~(1 << bit)
    _led_write()

def _set_gate_leds(open_low: bool, closed_low: bool) -> None:
    """Map state to LEDs: GREEN when open, RED when closed."""
    if closed_low:
        _led_on(LED_BIT_CLOSED)
        _led_off(LED_BIT_OPEN)
    elif open_low:
        _led_on(LED_BIT_OPEN)
        _led_off(LED_BIT_CLOSED)
    else:
        # in-between → both off (can change to blink if you want)
        _led_off(LED_BIT_OPEN)
        _led_off(LED_BIT_CLOSED)


# -------------------------- MOTOR ------------------------------------ #

def _enable(dist: Distributor, on: bool) -> None:
    dist.set_enable(MOTOR_ID, bool(on))

def _set_dir(dist: Distributor, dir_bit: int) -> None:
    dist.set_dir(MOTOR_ID, dir_bit)

def _step(dist: Distributor) -> None:
    dist.step(MOTOR_ID)

def _move_until_open(dist: Distributor) -> None:
    """Enable, run CW until OPEN (pin 34) goes LOW; then disable."""
    open_low, closed_low = _limits_low()
    _set_gate_leds(open_low, closed_low)
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
            _set_gate_leds(open_low, closed_low)
            break
        if open_low and closed_low:
            print("Both limits LOW! Safety stop.")
            _set_gate_leds(open_low, closed_low)
            break
        now = time.monotonic()
        if now < next_t:
            time.sleep(next_step := (next_t - now))
        _step(dist)
        next_t += STEP_INTERVAL_S

    _enable(dist, False)

def _move_until_closed(dist: Distributor) -> None:
    """Enable, run CCW until CLOSED (pin 33) goes LOW; then disable."""
    open_low, closed_low = _limits_low()
    _set_gate_leds(open_low, closed_low)
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
            _set_gate_leds(open_low, closed_low)
            break
        if open_low and closed_low:
            print("Both limits LOW! Safety stop.")
            _set_gate_leds(open_low, closed_low)
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
        return volts > SAW_OFF_THRESH_V
    return volts >= SAW_ON_THRESH_V


# --------------------------- MAIN LOOP -------------------------------- #

def main() -> None:
    dist = Distributor()
    atexit.register(dist.close)
    dist.reset()

    # Ensure no holding torque at idle
    _enable(dist, False)

    # Initialize LEDs to current limit state at startup
    open_low, closed_low = _limits_low()
    _set_gate_leds(open_low, closed_low)

    chan0 = _init_ads()
    print(
        "Auto-gate + LEDs: CH0 controls Motor 1; LEDs on 0x20 "
        "(bit0 GREEN=open, bit4 RED=closed).\n"
        "Limits: OPEN=34 LOW, CLOSED=33 LOW. No debounce, instant stop.\n"
        f"Hysteresis: on>={SAW_ON_THRESH_V:.3f} V, "
        f"off<={SAW_OFF_THRESH_V:.3f} V."
    )

    saw_on = False
    last_print = time.monotonic()

    try:
        while True:
            v = chan0.voltage
            new_state = _saw_state(v, saw_on)

            # Edge: OFF -> ON => open gate
            if not saw_on and new_state:
                print(f"Tablesaw ON (V={v:.3f}). Opening gate.")
                _move_until_open(dist)
                # Refresh LEDs to final state
                open_low, closed_low = _limits_low()
                _set_gate_leds(open_low, closed_low)

            # Edge: ON -> OFF => close gate
            if saw_on and not new_state:
                print(f"Tablesaw OFF (V={v:.3f}). Closing gate.")
                _move_until_closed(dist)
                open_low, closed_low = _limits_low()
                _set_gate_leds(open_low, closed_low)

            saw_on = new_state

            # Heartbeat (and ensure LEDs reflect whatever state we’re in)
            if time.monotonic() - last_print >= 2.0:
                last_print = time.monotonic()
                state = "ON " if saw_on else "OFF"
                open_low, closed_low = _limits_low()
                _set_gate_leds(open_low, closed_low)
                print(f"[hb] saw={state} V={v:.3f}  "
                      f"open_low={open_low} closed_low={closed_low}")

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
        # Turn both LEDs off (optional)
        _led_off(LED_BIT_OPEN)
        _led_off(LED_BIT_CLOSED)
        print("Stopped. Drivers disabled.")


if __name__ == "__main__":
    main()
