"""
A module for simplifying limiting the rate of a function call or hot loop.
"""

# built-in
from logging import INFO as _INFO
from typing import Callable as _Callable
from typing import Tuple as _Tuple

# internal
from vcorelib.math.analysis.rate import RateTracker as _RateTracker
from vcorelib.math.time import LoggerType as _LoggerType
from vcorelib.math.time import default_time_ns as _default_time_ns


class RateLimiter:
    """A class for limiting the rate of runtime work."""

    def __init__(self, period_ns: int, **kwargs) -> None:
        """Initialize this rate-limiter."""

        assert period_ns >= 0
        self.period_ns = period_ns
        self.prev_time_ns: int = 0
        self.rate = _RateTracker(**kwargs)
        self.skips: int = 0

    @property
    def rate_hz(self) -> float:
        """
        Get the underlying rate that this limiter is governing. This is useful
        to determine if the rate limitation is or isn't impacting the rate of
        some task.
        """
        return self.rate.value

    def dispatch(self) -> None:
        """A dispatch method that will be rate-limited."""

    def ready(self, time_ns: int = None) -> _Tuple[bool, int]:
        """Return whether or not this task is ready to run."""

        # Use a default time if one wasn't provided.
        if time_ns is None:
            time_ns = _default_time_ns()

        return time_ns >= self.prev_time_ns + self.period_ns, time_ns

    def __call__(
        self, time_ns: int = None, task: _Callable[[], None] = None
    ) -> bool:
        """
        Query the limiter to determine if the current time would allow a
        governed task to run.
        """

        result, time_ns = self.ready(time_ns)
        if result:
            self.prev_time_ns = time_ns

            self.dispatch()

            # Call the task if provided.
            if task is not None:
                task()

            # Update rate tracking.
            self.rate(time_ns=time_ns)
        else:
            self.skips += 1

        return result

    def log(
        self,
        log: _LoggerType,
        message: str,
        *args,
        level: int = _INFO,
        time_ns: int = None,
        **kwargs,
    ) -> None:
        """TODO."""

        result, time_ns = self.ready(time_ns)
        if result:
            pass

        print(log)
        print(message)
        print(args)
        print(level)
        print(time_ns)
        print(kwargs)
