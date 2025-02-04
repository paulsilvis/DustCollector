"""A simple Timer class"""

import time


class Timer:
    """A simple timer class with a timeout argument."""

    def __init__(self):
        """Initially no timer is set."""
        self.timer = None
        self.timeout = 0

    def clear_timer(self):
        """Remove the timer; it is now considered timedout"""
        if self.timer:
            print("Timer cleared")
        self.timer = None

    def set_timer(self, timeout):
        """Set the timer to expire in 'timeout' seconds"""
        self.timer = time.time()
        self.timeout = timeout
        print("Timer set")

    def check_timer_expired(self):
        """Return True and clear timer if it was running and is now
        expired.  Otherwise, return False."""
        if self.timer and (time.time() - self.timer >= self.timeout):
            self.clear_timer()
            return True
        return False
