"""
A module for managing runtime enumerations.
"""

# built-in
from typing import Dict as _Dict
from typing import NamedTuple
from typing import Optional as _Optional
from typing import Union as _Union
from typing import cast as _cast

# internal
from vcorelib.dict.codec import DictCodec as _DictCodec
from vcorelib.enum import BY_TYPE as _BY_TYPE
from vcorelib.enum import BoolRuntimeEnum as _BoolRuntimeEnum
from vcorelib.enum import EnumType as _EnumType
from vcorelib.enum import EnumTypelike as _EnumTypelike
from vcorelib.enum import IntRuntimeEnum as _IntRuntimeEnum
from vcorelib.enum import RuntimeEnum as _RuntimeEnum
from vcorelib.enum import RuntimeEnumType as _RuntimeEnumType
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue
from vcorelib.schemas import json_schemas as _json_schemas
from vcorelib.schemas.base import SchemaMap as _SchemaMap


class ManagedEnum(NamedTuple):
    """An enum wrapper for keeping track of an integer identifier and type."""

    id: int
    type: _EnumType
    items: _RuntimeEnumType

    def asdict(self) -> _JsonValue:
        """Get this managed enum as a dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "items": self.items.mapping,  # type: ignore
        }

    @staticmethod
    def from_dict(data: _JsonObject) -> "ManagedEnum":
        """Create a managed enumeration from dictionary data."""

        kind = _EnumType.normalize(_cast(str, data["type"]))
        return ManagedEnum(
            _cast(int, data["id"]), kind, _BY_TYPE[kind](mapping=data["items"])
        )


EnumMapping = _Dict[str, ManagedEnum]
RegistryKey = _Union[str, int]


class EnumRegistry(_DictCodec):
    """A class for managing runtime enumerations by name."""

    default_schemas: _Optional[_SchemaMap] = _json_schemas()

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        # Create enumeration objects.
        self.enums: EnumMapping = {
            name: ManagedEnum.from_dict(_cast(_JsonObject, enum))
            for name, enum in data.items()
        }

        self.current = 1

        # Assign each enumeration an integer value.
        self.mapping: _Dict[int, str] = {}
        self.reverse: _Dict[str, int] = {}

        # Keep track of existing enumerations
        for name, enum in self.enums.items():
            self.mapping[enum.id] = name
            self.reverse[name] = enum.id
            if enum.id >= self.current:
                self.current = enum.id + 1

    def asdict(self) -> _JsonObject:
        """Obtain a dictionary representing this instance."""
        return {name: enum.asdict() for name, enum in self.enums.items()}

    def _register_name(self, name: str) -> _Optional[int]:
        """Register a new enum name."""

        result = _RuntimeEnum.validate_name(name, strict=False)
        result &= name not in self.reverse

        identifier = None
        if result:
            # Ensure identifiers can never collide.
            while self.current in self.mapping:
                self.current += 1
            identifier = self.current

            self.reverse[name] = identifier
            self.mapping[identifier] = name

        return identifier

    def _assert_exists(self, name: str) -> ManagedEnum:
        """Verify that an enum exists and return it."""
        assert name in self.enums, f"No enum '{name}'!"
        return self.enums[name]

    def register(
        self, name: str, kind: _EnumTypelike, enum: _RuntimeEnumType
    ) -> ManagedEnum:
        """Register a new enumeration."""

        identifier = self._register_name(name)
        assert identifier is not None, f"Invalid name '{name}'!"

        # Verify that the kind and enum instance agree.
        kind = _EnumType.normalize(kind)
        assert enum.is_kind(kind), "Enum isn't '{kind}' type!"

        result = ManagedEnum(identifier, kind, enum)
        self.enums[name] = result
        return result

    def get_bool(self, val: RegistryKey) -> _BoolRuntimeEnum:
        """Access a boolean enumeration."""

        result = self.get_enum(val)
        assert isinstance(result, _BoolRuntimeEnum)
        return result

    def register_bool(
        self,
        name: str,
        mapping: _Dict[str, bool] = None,
        reverse: _Dict[bool, str] = None,
    ) -> _BoolRuntimeEnum:
        """Register a boolean enumeration."""

        result = _BoolRuntimeEnum(mapping=mapping, reverse=reverse)
        self.register(name, _EnumType.BOOL, result)
        return result

    def get_int(self, val: RegistryKey) -> _IntRuntimeEnum:
        """Access an integer enumeration."""

        result = self.get_enum(val)
        assert isinstance(result, _IntRuntimeEnum)
        return result

    def get_enum(self, val: RegistryKey) -> _RuntimeEnumType:
        """Get an enumeration by string name or integer identifier."""

        if isinstance(val, int):
            assert val in self.mapping, f"No enum identifier {val}!"
            val = self.mapping[val]
        return self._assert_exists(val).items

    def register_int(
        self,
        name: str,
        mapping: _Dict[str, int] = None,
        reverse: _Dict[int, str] = None,
    ) -> _IntRuntimeEnum:
        """Register an integer enumeration."""

        result = _IntRuntimeEnum(mapping=mapping, reverse=reverse)
        self.register(name, _EnumType.INT, result)
        return result
