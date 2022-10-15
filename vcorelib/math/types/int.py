"""
A module implementing a type interface for integers.
"""

# built-in
import ctypes as _ctypes
from typing import Dict as _Dict
from typing import Type as _Type
from typing import Union as _Union

# internal
from vcorelib.math.types import IntCtype as _IntCtype
from vcorelib.math.types import PrimitiveType as _PrimitiveType
from vcorelib.math.types.primitive import Primitive as _Primitive

# Type aliases.
Int8Type = _ctypes.c_byte
Int16Type = _ctypes.c_short
Int32Type = _ctypes.c_int
Int64Type = _ctypes.c_longlong
Uint8Type = _ctypes.c_ubyte
Uint16Type = _ctypes.c_ushort
Uint32Type = _ctypes.c_uint
Uint64Type = _ctypes.c_ulonglong


class IntegerType(_PrimitiveType):
    """A simple type interface for discretely sized integer types."""

    # 'struct' format specifiers.
    formats: _Dict[str, str] = {
        "int8": "b",
        "int16": "h",
        "int32": "i",
        "int64": "q",
        "uint8": "B",
        "uint16": "H",
        "uint32": "I",
        "uint64": "Q",
    }

    # Compatible C (language) type.
    cytpes: _Dict[str, _Type[_IntCtype]] = {
        "int8": Int8Type,
        "int16": Int16Type,
        "int32": Int32Type,
        "int64": Int64Type,
        "uint8": Uint8Type,
        "uint16": Uint16Type,
        "uint32": Uint32Type,
        "uint64": Uint64Type,
    }

    def __init__(self, size_bits: int, signed: bool) -> None:
        """Initialize this integer type."""

        self.size_bits = size_bits
        self.signed = signed
        self.name = f"{'u' if not self.signed else ''}int{self.size_bits}"

        assert (
            self.name in IntegerType.formats
        ), f"Un-supported bit width {size_bits}!"
        super().__init__(
            IntegerType.cytpes[self.name], IntegerType.formats[self.name]
        )
        assert self.is_integer

        # Set a minimum value.
        self.min = 0 if not self.signed else -1 * (2 ** (self.size_bits - 1))

        # Set a maximum value.
        self.max = (
            2
            ** (self.size_bits if not self.signed else 8 * self.size_bits - 1)
        ) - 1

    @staticmethod
    def unsigned_type(size_bits: int) -> "IntegerType":
        """A simple factory for unsigned integer types."""
        return IntegerType(size_bits, False)

    @staticmethod
    def signed_type(size_bits: int) -> "IntegerType":
        """A simple factory for signed integer types."""
        return IntegerType(size_bits, True)


INT8 = IntegerType.signed_type(8)


class Int8Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    raw: Int8Type

    def __init__(self, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(INT8)
        self.raw.value = value


INT16 = IntegerType.signed_type(16)


class Int16Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    raw: Int16Type

    def __init__(self, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(INT16)
        self.raw.value = value


INT32 = IntegerType.signed_type(32)


class Int32Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    raw: Int32Type

    def __init__(self, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(INT32)
        self.raw.value = value


INT64 = IntegerType.signed_type(64)


class Int64Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    raw: Int64Type

    def __init__(self, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(INT64)
        self.raw.value = value


UINT8 = IntegerType.unsigned_type(8)


class Uint8Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    raw: Uint8Type

    def __init__(self, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(UINT8)
        self.raw.value = value


UINT16 = IntegerType.unsigned_type(16)


class Uint16Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    raw: Uint16Type

    def __init__(self, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(UINT16)
        self.raw.value = value


UINT32 = IntegerType.unsigned_type(32)


class Uint32Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    raw: Uint32Type

    def __init__(self, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(UINT32)
        self.raw.value = value


UINT64 = IntegerType.unsigned_type(64)


class Uint64Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    raw: Uint64Type

    def __init__(self, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(UINT64)
        self.raw.value = value


IntegerPrimitive = _Union[
    Int8Primitive,
    Int16Primitive,
    Int32Primitive,
    Int64Primitive,
    Uint8Primitive,
    Uint16Primitive,
    Uint32Primitive,
    Uint64Primitive,
]
