"""
A module implementing a channel interface.
"""

# built-in
from typing import NamedTuple
from typing import Optional as _Optional
from typing import cast as _cast

# internal
from vcorelib.dict import GenericStrDict as _GenericStrDict
from vcorelib.enum.registry import RegistryKey as _RegistryKey
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue
from vcorelib.math.types.enum import PrimitiveTypes as _PrimitiveTypes
from vcorelib.math.types.enum import normalize_type as _normalize_type


class Channel(NamedTuple):
    """Attributes describing an individual channel."""

    id: int
    type: _PrimitiveTypes
    commandable: bool = False
    enum: _Optional[_RegistryKey] = None

    @property
    def is_enum(self) -> bool:
        """Determine if this channel has an associated enumeration."""
        return self.enum is not None

    def __eq__(self, other) -> bool:
        """Use our identifier for equivalence."""
        return bool(self.id == other.id)

    def __hash__(self) -> int:
        """Use our identifier as a hash."""
        return hash(self.id)

    def asdict(self) -> _JsonValue:
        """Get this channel as a dictionary."""

        result = {
            "id": self.id,
            "type": str(self.type),
            "commandable": self.commandable,
        }
        if self.enum is not None:
            result["enum"] = self.enum
        return result  # type: ignore

    @staticmethod
    def from_dict(data: _JsonObject) -> "Channel":
        """Create a channel from dictionary data."""

        casted = _cast(_GenericStrDict, data)
        return Channel(
            casted["id"],
            _normalize_type(casted["type"]),
            casted.get("commandable", False),
            casted.get("enum"),
        )
