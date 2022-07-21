"""
A module for working with averages.
"""

# built-in
from typing import List as _List


class MovingAverage:
    """A class for managing a moving average of floats."""

    def __init__(self, depth: int = 10, initial: float = 0.0) -> None:
        """Initialize this moving average."""

        self.index: int = 0
        self.depth: int = depth
        self.data: _List[float] = []
        self.sum: float = initial
        self.value: float = initial
        self.max: float = initial
        self.min: float = initial
        self.reset(initial=initial)

    def __call__(self, value: float) -> float:
        """Add a new value to the dataset and get the average."""

        # Remove the oldest value.
        self.sum -= self.data[self.index]

        # Add the new value.
        self.sum += value

        # Calculate the new average.
        self.value = self.sum / self.depth
        self.max = max(self.max, self.value)
        self.min = min(self.min, self.value)

        # Leave the new value behind.
        self.data[self.index] = value
        self.index += 1
        self.index %= self.depth

        return self.value

    def reset(self, initial: float = 0.0) -> None:
        """Reset the average value."""
        self.data = [initial for _ in range(self.depth)]
        self.sum = sum(self.data)
        self.value = self.sum / self.depth
        self.max = initial
        self.min = initial

    def resize(self, depth: int, initial: float = 0.0) -> None:
        """Set a new depth for this moving average and reset the value."""
        self.depth = depth
        self.reset(initial=initial)
