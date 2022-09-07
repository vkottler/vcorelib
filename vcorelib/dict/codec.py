"""
A module for implementing classes that can be loaded from dictionaries and
exported as dictionaries.
"""

# built-in
import abc as _abc
from typing import Type as _Type
from typing import TypeVar as _TypeVar

# internal
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io import DataArbiter as _DataArbiter
from vcorelib.io.types import EncodeResult as _EncodeResult
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.schemas.base import SchemaMap as _SchemaMap
from vcorelib.schemas.mixins import SchemaMixin

T = _TypeVar("T", bound="DictCodec")


class DictCodec(_abc.ABC):
    """
    A class implementing an interface for objects that can be decoded from
    disk and encoded back to disk.
    """

    @_abc.abstractmethod
    def __init__(self, data: dict) -> None:
        """Initialize this instance."""

    @_abc.abstractmethod
    def to_dict(self) -> dict:
        """Obtain a dictionary representing this instance."""

    def encode(
        self, pathlike: _Pathlike, arbiter: _DataArbiter = _ARBITER, **kwargs
    ) -> _EncodeResult:
        """Encode this object instance to a file."""
        return arbiter.encode(pathlike, self.to_dict(), **kwargs)

    @classmethod
    def decode(
        cls: _Type[T],
        pathlike: _Pathlike,
        arbiter: _DataArbiter = _ARBITER,
        **kwargs
    ) -> T:
        """Decode an object instance from data loaded from a file."""
        result = arbiter.decode(pathlike, require_success=True, **kwargs)
        return cls(result.data)


V = _TypeVar("V", bound="ValidatedDictCodec")


class BasicDictCodec(DictCodec):
    """The simplest possible dictionary codec implementation."""

    def __init__(self, data: dict) -> None:
        """Initialize this instance."""
        self.data = data

    def to_dict(self) -> dict:
        """Obtain a dictionary representing this instance."""
        return self.data


class ValidatedDictCodec(SchemaMixin):
    """
    A class that integrates class-based schema validation with dict-codec
    object instances.

    In practice this should enable creating object instances from data loaded
    from disk that's validated by a schema that also came from data loaded from
    disk.
    """

    def __init__(
        self,
        inst: DictCodec,
        schemas: _SchemaMap,
        valid_attr: str = "data",
    ) -> None:
        """Initialize this instance."""

        # Store the underlying instance.
        self.inst = inst

        # Validate the instance's dictionary data based on a schema.
        setattr(self, valid_attr, self.to_dict())
        super().__init__(schemas, valid_attr=valid_attr)

    @property
    def schema_name(self) -> str:
        """A default name for this class's schema."""
        return self.inst.__class__.__name__

    def to_dict(self) -> dict:
        """Get the underlying instance's dictionary."""
        return self.inst.to_dict()

    def encode(self, pathlike: _Pathlike, **kwargs) -> _EncodeResult:
        """Encode this object instance to a file."""
        return self.inst.encode(pathlike, **kwargs)

    @classmethod
    def decode(
        cls: _Type[V],
        codec: _Type[DictCodec],
        pathlike: _Pathlike,
        schemas: _SchemaMap,
        **kwargs
    ) -> V:
        """Decode an object instance from data loaded from a file."""
        return cls(codec.decode(pathlike, **kwargs), schemas)
