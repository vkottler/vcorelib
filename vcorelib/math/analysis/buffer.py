"""
A simple circular buffer for floating-point numbers.
"""

# built-in
from typing import List as _List

DEFAULT_DEPTH = 10


class FloatBuffer:
    """A class implementing a simple circular buffer for floats."""

    def __init__(
        self, depth: int = DEFAULT_DEPTH, initial: float = 0.0
    ) -> None:
        """Initialize this instance."""

        self._index: int = 0
        self.data: _List[float] = []
        self.depth: int = depth

        self.reset(initial=initial)

    def __call__(self, value: float) -> float:
        """
        Insert an element into the buffer and return the oldest value (that
        gets overwritten).
        """

        buf_idx = self._index % self.depth

        oldest = self.data[buf_idx]
        self.data[buf_idx] = value

        self._index += 1

        return oldest

    def reset(self, initial: float = 0.0) -> None:
        """Reset the buffer."""
        self.data = [initial for _ in range(self.depth)]

    def resize(self, depth: int, initial: float = 0.0) -> None:
        """Set a new depth for this buffer average and reset the values."""
        self.depth = depth
        self.reset(initial=initial)
