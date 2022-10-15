"""
A module implementing a simple type system for primitive values.
"""

# built-in
import ctypes as _ctypes
from struct import calcsize as _calcsize
from typing import Type as _Type
from typing import Union as _Union
from typing import cast as _cast

# Integer types.
SignedIntCtype = _Union[
    _ctypes.c_byte,
    _ctypes.c_short,
    _ctypes.c_int,
    _ctypes.c_long,
    _ctypes.c_longlong,
]
UnsignedIntCtype = _Union[
    _ctypes.c_ubyte,
    _ctypes.c_ushort,
    _ctypes.c_uint,
    _ctypes.c_ulong,
    _ctypes.c_ulonglong,
]
IntCtype = _Union[SignedIntCtype, UnsignedIntCtype]

# Floating-point types.
FloatCtype = _Union[_ctypes.c_float, _ctypes.c_double]

# Boolean type.
BoolCtype = _ctypes.c_bool

# All primitive types.
PrimitiveCtype = _Union[IntCtype, FloatCtype, BoolCtype]


class PrimitiveType:
    """A simple wrapper around ctype primitives."""

    name: str

    def __init__(
        self, c_type: _Type[PrimitiveCtype], struct_format: str
    ) -> None:
        """Initialize this primitive type."""

        self.c_type = c_type
        self.format = struct_format

        # Make sure that the struct size and ctype size match.
        self.size = _calcsize(self.format)
        c_type_size = _ctypes.sizeof(self.c_type)
        assert self.size == c_type_size, "{self.size} != {c_type_size}!"

        self.is_boolean = self.c_type == _ctypes.c_bool
        self.is_float = any(
            self.c_type == x for x in [_ctypes.c_float, _ctypes.c_double]
        )
        self.is_integer = (not self.is_boolean) and (not self.is_float)

    def __str__(self) -> str:
        """Get this type as a string."""
        return self.name

    def __hash__(self) -> int:
        """Get a hash for this type."""
        return hash(self.c_type)

    def __eq__(self, other) -> bool:
        """Determine if two types are equal."""
        if isinstance(other, PrimitiveType):
            other = other.c_type
        return _cast(bool, self.c_type == other)

    def get_int(self) -> IntCtype:
        """Get an integer primitive instance."""
        assert self.is_integer
        return _cast(IntCtype, self.instance())

    def get_bool(self) -> BoolCtype:
        """Get a boolean primitive instance."""
        assert self.is_boolean
        return _cast(BoolCtype, self.instance())

    def get_float(self) -> FloatCtype:
        """Get a floating-point primitive instance."""
        assert self.is_float
        return _cast(FloatCtype, self.instance())

    def instance(self) -> PrimitiveCtype:
        """Get an instance of this primitive type."""
        return self.c_type()
