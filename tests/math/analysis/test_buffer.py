"""
Test the 'math.analysis.buffer' module.
"""

# module under test
from vcorelib.math.analysis.buffer import FloatBuffer


def test_float_buffer_basic():
    """Test basic interactions with a circular buffer."""

    buffer = FloatBuffer()
    assert not buffer.saturated

    buffer(1.0)
    assert not buffer.saturated

    for _ in range(buffer.depth - 2):
        buffer(1.0)
    assert not buffer.saturated

    buffer(1.0)
    assert buffer.saturated

    buffer.reset()
    assert not buffer.saturated
