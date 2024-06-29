"""
A module for simplifying limiting the rate of a function call or hot loop.
"""

# built-in
from typing import Callable as _Callable

# internal
from vcorelib.math.analysis.rate import RateTracker as _RateTracker
from vcorelib.math.constants import to_nanos


class RateLimiter:
    """A class for limiting the rate of runtime work."""

    def __init__(self, period_ns: int, **kwargs) -> None:
        """Initialize this rate-limiter."""

        assert period_ns >= 0
        self.period_ns = period_ns
        self.prev_time_ns: int = 0
        self.rate = _RateTracker(**kwargs)
        self._skips: int = 0

    @staticmethod
    def from_s(period_s: float, **kwargs) -> "RateLimiter":
        """Create a rate limiter from seconds."""
        return RateLimiter(to_nanos(period_s), **kwargs)

    @property
    def rate_hz(self) -> float:
        """
        Get the underlying rate that this limiter is governing. This is useful
        to determine if the rate limitation is or isn't impacting the rate of
        some task.
        """
        return self.rate.value

    @property
    def skips(self) -> int:
        """Get the number of accumulated skips (due to rate limiting)."""

        result = self._skips
        self._skips = 0
        return result

    def __call__(
        self, time_ns: int = None, task: _Callable[[], None] = None
    ) -> bool:
        """
        Query the limiter to determine if the current time would allow a
        governed task to run.
        """

        result = False

        # Use a default time if one wasn't provided.
        if time_ns is None:
            time_ns = self.rate.source()

        if time_ns >= self.prev_time_ns + self.period_ns:
            self.prev_time_ns = time_ns
            result = True

            # Call the task if provided.
            if task is not None:
                task()

            # Update rate tracking.
            self.rate(time_ns=time_ns)

        else:
            self._skips += 1

        return result
