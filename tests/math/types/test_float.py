"""
Test the 'math.types.float' module.
"""

# module under test
from vcorelib.math.types.float import DoublePrimitive, FloatPrimitive


def test_float_primitive_basic():
    """
    Test simple interactions with a (single-precision) floating-point
    primitive.
    """

    test = FloatPrimitive()
    assert test == 0.0


def test_double_primitive_basic():
    """
    Test simple interactions with a (double-precision) floating-point
    primitive.
    """

    test = DoublePrimitive()
    assert test == 0.0
