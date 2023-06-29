"""
A module for implementing a weighted average.
"""

# internal
from vcorelib.math.analysis.average import MovingSum as _MovingSum
from vcorelib.math.analysis.buffer import DEFAULT_DEPTH as _DEFAULT_DEPTH
from vcorelib.math.analysis.buffer import FloatBuffer as _FloatBuffer


class WeightedAverage:
    """A class implementing a weighted average."""

    def __init__(self, depth: int = _DEFAULT_DEPTH) -> None:
        """Initialize this weighted average."""

        self.signals = _FloatBuffer(depth=depth)
        self.weights = _MovingSum(depth=depth)

    @property
    def depth(self) -> int:
        """This average's depth."""
        return self.signals.depth

    def reset(self) -> None:
        """Reset the average."""
        self.signals.reset()
        self.weights.reset()

    def average(self) -> float:
        """Compute the overall weighted average."""

        total: float = 0.0

        if self.weights.sum:
            for signal, weight in zip(self.signals.data, self.weights.data):
                # If an element has no weight, it shouldn't be considered.
                if weight > 0.0:
                    total += signal * (weight / self.weights.sum)

        return total

    def __call__(self, value: float, weight: float = 1.0) -> None:
        """Update tracking, doesn't compute weighted average."""

        self.signals(value)
        self.weights(weight)
