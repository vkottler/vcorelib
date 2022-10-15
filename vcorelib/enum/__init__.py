"""
A module implementing an enumeration-value interface for channels.
"""

# built-in
from enum import Enum as _Enum
from re import compile as _compile
from typing import Dict as _Dict
from typing import Generic as _Generic
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# internal
from vcorelib.mixins import RegexMixin as _RegexMixin

T = _TypeVar("T", int, bool)
EnumTypelike = _Union[str, "EnumType"]


class EnumType(_Enum):
    """An enumeration containing the types of runtime enumerations."""

    BOOL = "bool"
    INT = "int"

    def __str__(self) -> str:
        """Get this enum type as a string."""
        return self.value

    def validate(self, val: _Union[int, bool], strict: bool = True) -> bool:
        """Validate a primitive value."""

        result = isinstance(val, bool if self is EnumType.BOOL else int)
        if strict:
            assert result, f"Value '{val}' is not {self.value}!"
        return result

    @staticmethod
    def normalize(val: EnumTypelike) -> "EnumType":
        """Normalize an enumeration type."""

        if isinstance(val, str):
            val = EnumType(val.lower())
        return val


class RuntimeEnum(_Generic[T], _RegexMixin):
    """An enumeration mapping for a channel."""

    # Note that this needs to be kept synchronized with the JSON schema (for
    # the registry).
    name_regex = _compile("^\\w+$")
    kind: EnumType

    def __eq__(self, other) -> bool:
        """Determine if two runtime enumerations are equal."""

        if isinstance(other, RuntimeEnum):
            other = other.mapping
        return bool(self.mapping == other)

    @classmethod
    def is_kind(cls, kind: EnumType) -> bool:
        """
        Determine if the provided enum type is the one that matches this class.
        """
        return cls.kind == kind

    def __init__(
        self, mapping: _Dict[str, T] = None, reverse: _Dict[T, str] = None
    ) -> None:
        """Initialize this enumeration."""

        self.mapping: _Dict[str, T] = {}
        self.reverse: _Dict[T, str] = {}

        if mapping is None:
            mapping = {}
        for key, value in mapping.items():
            self.add(key, value)

        if reverse is None:
            reverse = {}
        for value, key in reverse.items():
            self.add(key, value)

    def add(self, key: str, value: T) -> bool:
        """Add an enumeration entry."""

        result = self.validate_name(key, strict=False)
        result &= self.kind.validate(value, strict=False)

        if result and key not in self.mapping and value not in self.reverse:
            self.mapping[key] = value
            self.reverse[value] = key

        return result

    def as_str(self, value: _Union[str, T]) -> str:
        """Get an enumeration value as a string."""

        if isinstance(value, str):
            result = value
        else:
            assert value in self.reverse, f"No entry for value '{value}'!"
            result = self.reverse[value]
        return result

    def as_value(self, value: _Union[str, T]) -> T:
        """Get the underlying value for an enumeration."""

        if isinstance(value, str):
            assert value in self.mapping, f"No entry for string '{value}'!"
            result = self.mapping[value]
        else:
            result = value
        return result


class BoolRuntimeEnum(
    RuntimeEnum[bool]
):  # pylint: disable=too-few-public-methods
    """A class for boolean enumerations."""

    kind = EnumType.BOOL


class IntRuntimeEnum(
    RuntimeEnum[int]
):  # pylint: disable=too-few-public-methods
    """A class for integer enumerations."""

    kind = EnumType.INT


RuntimeEnumType = _Union[BoolRuntimeEnum, IntRuntimeEnum]
BY_TYPE = {EnumType.BOOL: BoolRuntimeEnum, EnumType.INT: IntRuntimeEnum}
