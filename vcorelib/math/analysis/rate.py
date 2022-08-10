"""
A module for analyzing data rates in the time domain.
"""

# internal
from vcorelib.math.analysis.average import MovingAverage
from vcorelib.math.time import default_time_ns


class RateTracker:
    """A class for managing rate information for some data channel."""

    def __init__(self, **kwargs) -> None:
        """Initialize this rate tracker."""

        self.average = MovingAverage(**kwargs)
        self.prev_time_ns: int = 0

    @property
    def value(self) -> float:
        """An accessor for the underlying value."""
        return self.average.value

    @property
    def min(self) -> float:
        """An accessor for the underlying min."""
        return self.average.min

    @property
    def max(self) -> float:
        """An accessor for the underlying max."""
        return self.average.max

    def __call__(self, time_ns: int = None, value: float = 1.0) -> float:
        """
        Submit new data to the rate tracker. If this function is called with
        default arguments, the returned value will reflect the rate that this
        method is being called in hertz.
        """

        result = 0.0

        # Use a default time if one wasn't provided.
        if time_ns is None:
            time_ns = default_time_ns()

        # Only start tracking when a second data point is encountered.
        if self.prev_time_ns != 0:
            assert time_ns > self.prev_time_ns

            # Consider 'value' as the amount of change since the last data
            # entry, so divide value by the change in time to get a rate.
            result = self.with_dt(
                float(time_ns - self.prev_time_ns) / 10e9, value=value
            )

        self.prev_time_ns = time_ns
        return result

    def with_dt(self, delta_s: float, value: float = 1.0) -> float:
        """Update this rate by directly providing the delta-time value."""
        return self.average(value / delta_s)

    def reset(self, initial: float = 0.0) -> None:
        """Reset this rate tracker."""
        self.average.reset(initial=initial)
        self.prev_time_ns = 0
