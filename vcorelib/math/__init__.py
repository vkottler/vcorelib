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
from vcorelib.math.keeper import SimulatedTime
from vcorelib.math.time import (
    TIMER,
    LoggerType,
    Timer,
    byte_count_str,
    default_time_ns,
    metrics_time_ns,
    nano_str,
    rate_str,
    restore_time_source,
    seconds_str,
    set_simulated_source,
    simulated_time,
)
from vcorelib.math.unit import KIBI_UNITS, SI_UNITS, UnitSystem, unit_traverse

__all__ = [
    "metrics_time_ns",
    "restore_time_source",
    "set_simulated_source",
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
    "simulated_time",
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
    "SimulatedTime",
]
