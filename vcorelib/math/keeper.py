"""
A module implementing a simple time-keeper interface.
"""

# built-in
from contextlib import contextmanager
from time import time_ns as _time_ns
from typing import Callable, Iterator

# internal
from vcorelib.math.constants import to_nanos

TimeSource = Callable[[], int]


class SimulatedTime:
    """A simple simulated-time interface."""

    def __init__(self, step_dt_ns: int, start_ns: int = 0) -> None:
        """Initialize this instance."""

        self._start_ns = start_ns
        self._step = 0

        assert step_dt_ns >= 1, step_dt_ns
        self._step_dt_ns = step_dt_ns

    def step(self, count: int = 1) -> None:
        """Step forward (or backwards) in time."""
        self._step += count

    def step_s(self, time_s: float) -> None:
        """Step some number of seconds."""
        self.step(to_nanos(time_s) // self._step_dt_ns)

    def __call__(self) -> int:
        """Get the current simulated time."""
        return self._start_ns + (self._step * self._step_dt_ns)


class TimeKeeper:
    """A simple nanosecond time keeping interface."""

    def __init__(self, source: TimeSource = _time_ns) -> None:
        """Initialize this instance."""

        self.source = source
        self.orig = self.source

    def restore(self) -> None:
        """Restore the original time source."""
        self.source = self.orig

    @contextmanager
    def simulated(
        self, step_dt_ns: int = 1, start_ns: int = None
    ) -> Iterator[SimulatedTime]:
        """Take over time resolution with a simulated time instance."""

        # Use a realistic starting timestamp value if one isn't provided.
        if start_ns is None:
            start_ns = self()

        sim_time = SimulatedTime(step_dt_ns, start_ns=start_ns)

        # Update 'source' to power simulated time resolution.
        self.source = sim_time

        try:
            yield sim_time
        finally:
            self.restore()

    def __call__(self) -> int:
        """Get time."""
        return self.source()


TIME = TimeKeeper()
