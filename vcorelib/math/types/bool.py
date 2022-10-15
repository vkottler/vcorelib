"""
A module implementing a type interface for booleans.
"""

# internal
from vcorelib.math.types import BoolCtype, PrimitiveType
from vcorelib.math.types.primitive import Primitive as _Primitive


class BooleanType(PrimitiveType):
    """A simple type interface for booleans."""

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__(BoolCtype, "?")
        assert self.is_boolean
        self.name = "bool"


BOOL = BooleanType()


class BooleanPrimitive(_Primitive[bool]):
    """A simple primitive class for booleans."""

    raw: BoolCtype

    def __init__(self, value: bool = False) -> None:
        """Initialize this boolean primitive."""
        super().__init__(BOOL)
        self.raw.value = value

    def toggle(self) -> None:
        """Toggle the underlying value."""
        self.raw.value = not self.raw.value

    def set(self) -> None:
        """Coerce the underlying value to true."""
        self.raw.value = True

    def clear(self) -> None:
        """Coerce the underlying value to false."""
        self.raw.value = False
