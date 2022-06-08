"""
A module implementing a JSON-file database.
"""

# built-in
from abc import ABC, abstractmethod
from contextlib import ExitStack as _ExitStack
from contextlib import contextmanager as _contextmanager
from typing import Iterator as _Iterator

# internal
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io import DataArbiter as _DataArbiter
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize as _normalize


class JsonCache(ABC):
    """A JSON cach interface."""

    def __init__(
        self, pathlike: _Pathlike, arbiter: _DataArbiter = _ARBITER
    ) -> None:
        """Initialize this cache."""
        self.path = _normalize(pathlike)
        self.arbiter = arbiter

    @abstractmethod
    def context_load(self, stack: _ExitStack, **kwargs) -> _JsonObject:
        """Load the data."""

    @_contextmanager
    def loaded(self, **kwargs) -> _Iterator[_JsonObject]:
        """
        Provide loaded data so that the data is written back to disk on
        completion.
        """
        with _ExitStack() as stack:
            yield self.context_load(stack, **kwargs)


class FileCache(JsonCache):
    """A class implementing a JSON cache based on a file."""

    def context_load(self, stack: _ExitStack, **kwargs) -> _JsonObject:
        """Load the data."""
        return stack.enter_context(
            self.arbiter.object_file_context(self.path, **kwargs)
        )


class DirectoryCache(JsonCache):
    """A class implementing a JSON cache based on a directory."""

    def context_load(self, stack: _ExitStack, **kwargs) -> _JsonObject:
        """Load the data."""
        return stack.enter_context(
            self.arbiter.object_directory_context(self.path, **kwargs)
        )
