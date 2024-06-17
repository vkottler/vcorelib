"""
A module for working with averages.
"""

# internal
from vcorelib.math.analysis.buffer import DEFAULT_DEPTH as _DEFAULT_DEPTH
from vcorelib.math.analysis.buffer import FloatBuffer as _FloatBuffer


class MovingSum(_FloatBuffer):
    """A simple moving sum implementation."""

    def __init__(
        self, depth: int = _DEFAULT_DEPTH, initial: float = 0.0
    ) -> None:
        """Initialize this instance."""

        self.sum: float = initial
        super().__init__(depth=depth, initial=initial)

    def __call__(self, value: float) -> float:
        """Update the moving sum."""

        self.sum -= super().__call__(value)
        self.sum += value
        return self.sum

    def reset(self, initial: float = 0.0) -> None:
        """Reset the buffer and sum."""

        super().reset(initial=initial)
        self.sum = sum(self.data)


class MovingAverage:
    """A class for managing a moving average of floats."""

    def __init__(
        self, depth: int = _DEFAULT_DEPTH, initial: float = 0.0
    ) -> None:
        """Initialize this moving average."""

        self.buffer = MovingSum(depth=depth, initial=initial)

        self._initialized = False

        # Intentionally public members.
        self.average: float = initial
        self.max: float = initial
        self.min: float = initial

        self.reset(initial=initial)

    def _update_min_max(self, value: float) -> None:
        """Update min-max tracking based on the provided value."""

        # Ensure that max and min don't retain an initial value.
        if not self._initialized:
            self.max = value
            self.min = value
            self._initialized = True
        else:
            self.max = max(self.max, value)
            self.min = min(self.min, value)

    def __call__(self, value: float) -> float:
        """Add a new value to the dataset and get the average."""

        self.average = self.buffer(value) / self.buffer.depth
        self._update_min_max(value)
        return self.average

    def reset(self, initial: float = 0.0) -> None:
        """Reset the average value."""

        self.buffer.reset(initial=initial)
        self.average = self.buffer.sum / self.buffer.depth
        self.max = initial
        self.min = initial
        self._initialized = False

    @property
    def saturated(self) -> bool:
        """Determine if the buffer is saturated with elements yet."""
        return self.buffer.saturated

    def resize(self, depth: int, initial: float = 0.0) -> None:
        """Set a new depth for this moving average and reset the value."""

        self.buffer.resize(depth, initial=initial)
        self.reset(initial=initial)
