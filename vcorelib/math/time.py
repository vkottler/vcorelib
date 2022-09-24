"""
Math utilities involving units of time and other conversions.
"""

# built-in
from contextlib import contextmanager
from io import StringIO
from logging import INFO as _INFO
from logging import Logger
from math import floor as _floor
from time import perf_counter_ns as _perf_counter_ns
from time import time_ns as _time_ns
from typing import Dict as _Dict
from typing import Iterator as _Iterator
from typing import Tuple as _Tuple

# internal
from vcorelib.math import KIBI_UNITS as _KIBI_UNITS
from vcorelib.math import SI_UNITS as _SI_UNITS
from vcorelib.math import UnitSystem as _UnitSystem
from vcorelib.math import unit_traverse as _unit_traverse


def default_time_ns() -> int:
    """Get a timestamp value using a default method."""
    return _time_ns()


def seconds_str(seconds: int) -> _Tuple[str, int]:
    """
    Attempt to characterize a large amount of seconds into a string describing
    hours and minutes, returning the string (may be empty) and the seconds
    left over.
    """

    result = ""

    minutes = 0
    if seconds >= 60:
        minutes = seconds // 60
        seconds = seconds % 60
        result = f"{minutes}m"

    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        result = f"{hours}h {minutes}m"

    return result, seconds


def nano_str(
    nanos: int,
    is_time: bool = False,
    max_prefix: int = 3,
    unit: _UnitSystem = _SI_UNITS,
    prefix_space: bool = False,
    iteration: int = 0,
) -> str:
    """
    Convert an arbitrary value in a 10^-9 domain into as concise of a string
    as possible.
    """

    decimal, fractional, prefix = _unit_traverse(
        nanos, unit, max_prefix, iteration
    )

    with StringIO() as stream:
        if not prefix and is_time:
            result, decimal = seconds_str(decimal)
            stream.write(result)
            if result:
                stream.write(" ")

        # Normalize the fractional component if necessary.
        if unit.divisor != 1000 and fractional != 0:
            fractional = _floor(float(fractional / unit.divisor) * 1000.0)

        stream.write(str(decimal))
        if fractional:
            stream.write(f".{fractional:03}")
        if prefix_space:
            stream.write(" ")
        stream.write(prefix)
        return stream.getvalue()


def byte_count_str(byte_count: int) -> str:
    """Get a string representing a number of bytes."""
    return nano_str(byte_count, False, 99, _KIBI_UNITS, True) + "B"


class Timer:
    """A class for measuring and logging how long events take."""

    def __init__(self) -> None:
        """Initialize this timer."""

        self.curr: int = 0
        self.data: _Dict[int, int] = {}

    @contextmanager
    def measure_ns(self) -> _Iterator[int]:
        """
        Compute the time that the caller's context takes, provides an integer
        token that can be used to query for the result afterwards.
        """

        curr = self.curr
        self.curr += 1
        start = _perf_counter_ns()
        try:
            yield curr
        finally:
            self.data[curr] = _perf_counter_ns() - start

    def result(self, token: int) -> int:
        """Get the timer result."""
        return self.data.pop(token, -1)

    @contextmanager
    def log(
        self,
        log: Logger,
        message: str,
        *args,
        level: int = _INFO,
        **kwargs,
    ) -> _Iterator[None]:
        """Log how long the caller's context took to execute."""

        with self.measure_ns() as token:
            yield
        result = self.result(token)

        # Log the duration spent yielded.
        log.log(
            level,
            message + " completed in %ss.",
            *args,
            nano_str(result, True),
            **kwargs,
        )


TIMER = Timer()
