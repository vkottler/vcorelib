"""
A module implementing a type interface for floating-point numbers.
"""

# built-in
import ctypes as _ctypes
from typing import Union as _Union

# internal
from vcorelib.math.types import PrimitiveType as _PrimitiveType
from vcorelib.math.types.primitive import Primitive as _Primitive


class FloatType(_PrimitiveType):
    """A simple type interface for single-precision floating-point."""

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__(_ctypes.c_float, "f")
        assert self.is_float
        self.name = "float"


FLOAT = FloatType()


class FloatPrimitive(_Primitive[float]):
    """A simple primitive class for single-precision floating-point."""

    raw: _ctypes.c_float

    def __init__(self, value: float = 0.0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(FLOAT, value=value)


class DoubleType(_PrimitiveType):
    """A simple type interface for double-precision floating-point."""

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__(_ctypes.c_double, "d")
        assert self.is_float
        self.name = "double"


DOUBLE = DoubleType()


class DoublePrimitive(_Primitive[float]):
    """A simple primitive class for double-precision floating-point."""

    raw: _ctypes.c_double

    def __init__(self, value: float = 0.0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(DOUBLE, value=value)


FloatingPointPrimitive = _Union[FloatPrimitive, DoublePrimitive]
