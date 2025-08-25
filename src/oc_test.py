# gate_limits_pcf.py
# Uses existing PCF8574_in drivers at 0x20..0x24.
# Debounces flat pins 34 (OPEN) and 33 (CLOSED), active-low.
# Prints edges + periodic status; can also be used as a library.
#
# Style: flake8 / black -l 79

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Tuple

from pcf8574_in import PCF8574_in


# ------------------------------ Config -------------------------------- #

OPEN_PIN = 34     # flat index: chip*8 + bit
CLOSED_PIN = 33   # flat index
DEBOUNCE_MS = 15
STATUS_PERIOD_S = 0.5
POLL_PERIOD_S = 0.002  # ~500 Hz


# ------------------------------ Helpers ------------------------------- #

def _pack_40(b0: int, b1: int, b2: int, b3: int, b4: int) -> int:
    """Pack five 8-bit chunks into a 40-bit little-endian value.

    b0 is flat pins 0..7 (addr 0x20), b1 => 8..15, ... b4 => 32..39.
    """
    return (b0 | (b1 << 8) | (b2 << 16) | (b3 << 24) | (b4 << 32))


def _bit_is_low(val: int, idx: int) -> bool:
    """Active-low: return True if flat pin idx is 0 (asserted)."""
    return ((val >> idx) & 1) == 0


@dataclass
class Debounce:
    ms: int = DEBOUNCE_MS
    _raw: int = 1
    _stable: int = 1
    _t0: float = time.monotonic()

    def force(self, level: int) -> None:
        self._raw = 1 if level else 0
        self._stable = self._raw
        self._t0 = time.monotonic()

    def update(self, level: int) -> Optional[int]:
        lvl = 1 if level else 0
        if lvl != self._raw:
            self._raw = lvl
            self._t0 = time.monotonic()
            return None  # edge seen; start debounce timer
        if self._stable != self._raw:
            if (time.monotonic() - self._t0) * 1000 >= self.ms:
                self._stable = self._raw
                return self._stable  # new stable level
            return None
        return self._stable

    @property
    def stable(self) -> int:
        return self._stable


class GateLimitsPCF:
    """Reads two flat pins from 5× PCF8574 and debounces them."""

    def __init__(self, open_idx: int = OPEN_PIN, closed_idx: int = CLOSED_PIN):
        self._open_idx = open_idx
        self._closed_idx = closed_idx

        # Five input expanders at 0x20..0x24 (your PCF8574_in wrapper)
        self._dev = [
            PCF8574_in(address=0x20 + i) for i in range(5)
        ]

        # Debouncers (active-low => asserted == 0)
        self._db_o = Debounce()
        self._db_c = Debounce()

        # Prime with current levels
        val = self._read_40()
        self._db_o.force(1 if not _bit_is_low(val, self._open_idx) else 0)
        self._db_c.force(1 if not _bit_is_low(val, self._closed_idx) else 0)

    def _read_40(self) -> int:
        b = [d.read_all() & 0xFF for d in self._dev]
        return _pack_40(*b)

    def update(self) -> Tuple[Optional[int], Optional[int], str]:
        """Poll once; return (open_level, closed_level, state).

        Levels are 0/1 where 0 = asserted (LOW), 1 = idle (HIGH).
        Returns None for a channel if it is still debouncing.
        """
        val = self._read_40()
        o_lvl_raw = 0 if _bit_is_low(val, self._open_idx) else 1
        c_lvl_raw = 0 if _bit_is_low(val, self._closed_idx) else 1

        o = self._db_o.update(o_lvl_raw)
        c = self._db_c.update(c_lvl_raw)

        state = (
            "Closed"
            if self._db_c.stable == 0
            else ("Open" if self._db_o.stable == 0 else "Moving")
        )
        return o, c, state

    @property
    def open_level(self) -> int:
        return self._db_o.stable  # 0 asserted, 1 idle

    @property
    def closed_level(self) -> int:
        return self._db_c.stable  # 0 asserted, 1 idle

    def gate_state(self) -> str:
        return (
            "Closed"
            if self.closed_level == 0
            else ("Open" if self.open_level == 0 else "Moving")
        )


def main() -> None:
    gl = GateLimitsPCF(OPEN_PIN, CLOSED_PIN)

    last_status = time.monotonic()
    try:
        while True:
            o, c, state = gl.update()

            ts = time.monotonic()
            if o is not None:
                print(
                    f"{ts:.3f} OPEN "
                    f"{'assert' if o == 0 else 'release'} -> {state}"
                )
            if c is not None:
                print(
                    f"{ts:.3f} CLOSED "
                    f"{'assert' if c == 0 else 'release'} -> {state}"
                )

            if ts - last_status >= STATUS_PERIOD_S:
                last_status = ts
                print(
                    f"{ts:.3f} Gate={state} | "
                    f"OPEN={'LOW' if gl.open_level == 0 else 'HIGH'} | "
                    f"CLOSED={'LOW' if gl.closed_level == 0 else 'HIGH'}"
                )

            time.sleep(POLL_PERIOD_S)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
