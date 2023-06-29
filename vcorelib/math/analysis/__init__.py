"""
A module for aggregating symbols for import.
"""

# internal
from vcorelib.math.analysis.average import MovingAverage, MovingSum
from vcorelib.math.analysis.buffer import DEFAULT_DEPTH, FloatBuffer
from vcorelib.math.analysis.rate import RateTracker, ns_to_s
from vcorelib.math.analysis.rate.limiter import RateLimiter
from vcorelib.math.analysis.weighted import WeightedAverage

__all__ = [
    "MovingAverage",
    "MovingSum",
    "WeightedAverage",
    "DEFAULT_DEPTH",
    "FloatBuffer",
    "ns_to_s",
    "RateTracker",
    "RateLimiter",
]
