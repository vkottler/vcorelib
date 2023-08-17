"""
A module implementing a simple bytes FIFO interface.
"""

# built-in
from typing import Optional as _Optional


class ByteFifo:
    """A simple fifo for bytes."""

    def __init__(self) -> None:
        """Initialize this instance."""

        self.data = bytes()
        self.size = 0

    def ingest(self, data: bytes) -> None:
        """Append new data to the end."""

        self.data += data
        self.size = len(self.data)

    def pop(self, size: int) -> _Optional[bytes]:
        """Attempt to read some number of bytes from the front."""

        result = None

        if self.size >= size:
            result = self.data[:size]

            self.data = self.data[size:]
            self.size -= size

        return result
