"""
Math utilities.
"""

# internal
from vcorelib.math.analysis import (
    DEFAULT_DEPTH,
    FloatBuffer,
    MovingAverage,
    MovingSum,
    WeightedAverage,
)
from vcorelib.math.analysis.rate import RateTracker
from vcorelib.math.analysis.rate.limiter import RateLimiter
from vcorelib.math.constants import BILLION, MILLION, from_nanos, to_nanos
from vcorelib.math.time import (
    TIMER,
    LoggerType,
    Timer,
    byte_count_str,
    default_time_ns,
    nano_str,
    rate_str,
    seconds_str,
)
from vcorelib.math.unit import KIBI_UNITS, SI_UNITS, UnitSystem, unit_traverse

__all__ = [
    "MILLION",
    "BILLION",
    "from_nanos",
    "to_nanos",
    "UnitSystem",
    "SI_UNITS",
    "KIBI_UNITS",
    "unit_traverse",
    "byte_count_str",
    "default_time_ns",
    "nano_str",
    "seconds_str",
    "rate_str",
    "LoggerType",
    "Timer",
    "TIMER",
    "DEFAULT_DEPTH",
    "MovingAverage",
    "RateLimiter",
    "RateTracker",
    "FloatBuffer",
    "MovingSum",
    "WeightedAverage",
]
