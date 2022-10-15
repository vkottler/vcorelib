"""
A module implementing an enumeration for all valid primitive types.
"""

# built-in
from enum import Enum as _Enum
from typing import Union as _Union

# internal
from vcorelib.math.types.bool import BooleanPrimitive as _BooleanPrimitive
from vcorelib.math.types.float import DoublePrimitive as _DoublePrimitive
from vcorelib.math.types.float import FloatPrimitive as _FloatPrimitive
from vcorelib.math.types.int import Int8Primitive as _Int8Primitive
from vcorelib.math.types.int import Int16Primitive as _Int16Primitive
from vcorelib.math.types.int import Int32Primitive as _Int32Primitive
from vcorelib.math.types.int import Int64Primitive as _Int64Primitive
from vcorelib.math.types.int import Uint8Primitive as _Uint8Primitive
from vcorelib.math.types.int import Uint16Primitive as _Uint16Primitive
from vcorelib.math.types.int import Uint32Primitive as _Uint32Primitive
from vcorelib.math.types.int import Uint64Primitive as _Uint64Primitive


class PrimitiveTypes(_Enum):
    """A simple enumeration for all valid primitive-type implementations."""

    BOOL = _BooleanPrimitive
    FLOAT = _FloatPrimitive
    DOUBLE = _DoublePrimitive

    # Integer types.
    INT8 = _Int8Primitive
    INT16 = _Int16Primitive
    INT32 = _Int32Primitive
    INT64 = _Int64Primitive
    UINT8 = _Uint8Primitive
    UINT16 = _Uint16Primitive
    UINT32 = _Uint32Primitive
    UINT64 = _Uint64Primitive

    def __str__(self) -> str:
        """Get this instance as a string."""
        return self.name.lower()


TYPES = {
    "bool": PrimitiveTypes.BOOL,
    "float": PrimitiveTypes.FLOAT,
    "double": PrimitiveTypes.DOUBLE,
    "int8": PrimitiveTypes.INT8,
    "int16": PrimitiveTypes.INT16,
    "int32": PrimitiveTypes.INT32,
    "int64": PrimitiveTypes.INT64,
    "uint8": PrimitiveTypes.UINT8,
    "uint16": PrimitiveTypes.UINT16,
    "uint32": PrimitiveTypes.UINT32,
    "uint64": PrimitiveTypes.UINT64,
}
PrimitiveTypelike = _Union[PrimitiveTypes, str]


def normalize_type(kind: PrimitiveTypelike) -> PrimitiveTypes:
    """Resolve a type's string name if necessary."""

    if isinstance(kind, str):
        return TYPES[kind]
    return kind
