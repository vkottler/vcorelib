"""
Test the 'math.types.bool' module.
"""

# built-in
from io import SEEK_CUR, BytesIO

# module under test
from vcorelib.math.types.bool import BooleanPrimitive


def test_boolean_primitive_basic():
    """Test simple interactions with a boolean primitive."""

    test = BooleanPrimitive()
    assert test == BooleanPrimitive()
    assert not test
    assert str(test) == "False"
    test.toggle()
    assert test

    test.set()
    assert test
    test.clear()
    assert not test

    # Encoding and decoding should consume one byte.
    size = 1

    test.set()

    with BytesIO() as stream:
        # Verify we encode 'true'.
        assert test.to_stream(stream) == size
        stream.seek(-1 * size, SEEK_CUR)
        test.from_stream(stream)
        assert test

        # Change the value.
        test.toggle()

        # Verify we encode 'false'.
        assert test.to_stream(stream) == size
        stream.seek(-1 * size, SEEK_CUR)
        test.from_stream(stream)
        assert not test
