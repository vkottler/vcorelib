"""
Math utilities involving units of time and other conversions.
"""

# built-in
from io import StringIO
from math import floor as _floor
from typing import Tuple as _Tuple

# internal
from vcorelib.math import KIBI_UNITS as _KIBI_UNITS
from vcorelib.math import SI_UNITS as _SI_UNITS
from vcorelib.math import UnitSystem as _UnitSystem
from vcorelib.math import unit_traverse as _unit_traverse


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
