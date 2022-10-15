"""
A module for integer-related math.
"""

# built-in
from math import isclose as _isclose
from struct import pack as _pack
from struct import unpack as _unpack
from typing import BinaryIO as _BinaryIO
from typing import Generic as _Generic
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# internal
from vcorelib.math.types import PrimitiveType as _PrimitiveType

T = _TypeVar("T", bool, int, float)


class Primitive(_Generic[T]):
    """A simple class for storing and underlying primitive value."""

    # Use network byte-order by default.
    byte_order = "!"

    def __str__(self) -> str:
        """Get this primitive's value as a string."""
        return str(self.raw.value)

    def __eq__(self, other) -> bool:
        """
        Determine if this instance is equivalent to the provided argument.
        """

        if isinstance(other, Primitive):
            other = other.raw.value

        if self.kind.is_float:
            return _isclose(self.raw.value, other)

        return bool(self.raw.value == other)

    def __bool__(self) -> bool:
        """Use the underlying value for boolean evaluation."""
        return bool(self.raw)

    def __init__(self, kind: _PrimitiveType = None, value: T = None) -> None:
        """Initialize this primitive."""

        assert kind is not None
        self.kind = kind
        self.raw = self.kind.instance()
        self(value=value)

    def __call__(self, value: T = None) -> T:
        """
        A callable interface for setting and getting the underlying value.
        """

        if value is not None:
            self.raw.value = value
        return self.raw.value  # type: ignore

    def __bytes__(self) -> bytes:
        """Convert this instance to a byte array."""
        return _pack(self.byte_order + self.kind.format, self.raw.value)

    def to_stream(self, stream: _BinaryIO) -> int:
        """Write this primitive to a stream."""
        stream.write(bytes(self))
        return self.kind.size

    def from_stream(self, stream: _BinaryIO) -> None:
        """Update this primitive from a stream."""
        self.raw.value = _unpack(
            self.byte_order + self.kind.format, stream.read(self.kind.size)
        )[0]


BooleanPrimitive = Primitive[bool]
FloatPrimitive = Primitive[float]
IntPrimitive = Primitive[int]
AnyPrimitive = _Union[BooleanPrimitive, FloatPrimitive, IntPrimitive]
