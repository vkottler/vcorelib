"""
Test the 'io.fifo' module.
"""

# module under test
from vcorelib.io import ByteFifo


def test_bytes_fifo_basic():
    """Test basic interaction with a bytes FIFO."""

    fifo = ByteFifo()

    assert fifo.pop(1) is None

    fifo.ingest(bytes(range(10)))

    assert fifo.pop(5) == bytes(range(5))

    assert fifo.pop(5)
