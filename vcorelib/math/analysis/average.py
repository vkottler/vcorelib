"""
A module for working with averages.
"""

# built-in
from typing import List as _List


class MovingAverage:  # pylint: disable=too-many-instance-attributes
    """A class for managing a moving average of floats."""

    def __init__(self, depth: int = 10, initial: float = 0.0) -> None:
        """Initialize this moving average."""

        self._index: int = 0
        self._data: _List[float] = []
        self._sum: float = initial

        # Intentionally public members.
        self.depth: int = depth
        self.value: float = initial
        self.max: float = initial
        self.min: float = initial

        self.reset(initial=initial)
        self._initialized = False

    def __call__(self, value: float) -> float:
        """Add a new value to the dataset and get the average."""

        # Remove the oldest value.
        self._sum -= self._data[self._index]

        # Add the new value.
        self._sum += value

        # Calculate the new average.
        self.value = self._sum / self.depth

        # Ensure that max and min don't retain an initial value.
        if not self._initialized:
            self.max = value
            self.min = value
            self._initialized = True
        else:
            self.max = max(self.max, value)
            self.min = min(self.min, value)

        # Leave the new value behind.
        self._data[self._index] = value
        self._index += 1
        self._index %= self.depth

        return self.value

    def reset(self, initial: float = 0.0) -> None:
        """Reset the average value."""

        self._data = [initial for _ in range(self.depth)]
        self._sum = sum(self._data)
        self.value = self._sum / self.depth
        self.max = initial
        self.min = initial
        self._initialized = False

    def resize(self, depth: int, initial: float = 0.0) -> None:
        """Set a new depth for this moving average and reset the value."""

        self.depth = depth
        self.reset(initial=initial)
