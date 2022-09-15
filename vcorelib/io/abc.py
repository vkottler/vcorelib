"""
A module for abstract base-classes relevant to IO.
"""

# built-in
import abc as _abc
from typing import TextIO as _TextIO

# internal
from vcorelib import DEFAULT_ENCODING as _DEFAULT_ENCODING
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize as _normalize


class Serializable(_abc.ABC):
    """An interface definition for serializable classes."""

    def default_location(self) -> _Pathlike:
        """Get a default serialization destination for this instance."""
        return f"{self.__class__.__name__}.txt"

    @_abc.abstractmethod
    def to_stream(self, stream: _TextIO, **kwargs) -> None:
        """Write this object to a text stream."""

    def to_file(
        self,
        path: _Pathlike = None,
        encoding: str = _DEFAULT_ENCODING,
        **kwargs,
    ) -> None:
        """Write this object to a file."""

        with _normalize(
            path if path is not None else self.default_location()
        ).open("w", encoding=encoding) as stream:
            self.to_stream(stream, **kwargs)
            stream.flush()


class FileEntity(Serializable):
    """A class for working with objects that are backed by a disk location."""

    def __hash__(self) -> int:
        """Use this instance's disk location for hashing."""
        return hash(self.location)

    def default_location(self) -> _Pathlike:
        """Get a default serialization destination for this instance."""
        return self.location

    def __init__(self, location: _Pathlike) -> None:
        """Initialize this file-backed entity."""
        assert not hasattr(self, "location")
        self.location = _normalize(location)
