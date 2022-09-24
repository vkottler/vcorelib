"""
A module for implementing a configuration data manager with a dictionary.
"""

# built-in
from collections import UserDict as _UserDict
from typing import Any as _Any
from typing import MutableMapping as _MutableMapping

# internal
from vcorelib.dict import GenericDict as _GenericDict
from vcorelib.dict import consume as _consume
from vcorelib.dict import merge as _merge
from vcorelib.dict import set_if_not as _set_if_not
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io.types import FileExtension as _FileExtension
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize as _normalize

ConfigData = _MutableMapping[str, _Any]


class Config(
    _UserDict,  # type: ignore
    ConfigData,
):
    """A dictionary that allows access to data only once via each key."""

    def __getitem__(self, key) -> _Any:
        """Consume keys after their data is retreived."""
        assert key in self.data, f"Key '{key}' not found in configuration!"
        return _consume(self.data, key)

    def get(self, key, default=None) -> _Any:
        """Get data from the configuration but allow a default value."""
        return _consume(self.data, key, default)

    def set_if_not(self, key, value) -> _Any:
        """Set this value if a value is not already set."""
        return _set_if_not(self.data, key, value)

    def merge(self, other: _GenericDict, *args, **kwargs) -> None:
        """Merge another dictionary into this one."""
        _merge(self.data, other, *args, **kwargs)

    @staticmethod
    def from_file(pathlike: _Pathlike, *args, **kwargs) -> "Config":
        """Load a configuration from a file on disk."""
        _set_if_not(kwargs, "require_success", True)
        return Config(_ARBITER.decode(pathlike, *args, **kwargs).data)

    @staticmethod
    def from_directory(pathlike: _Pathlike, *args, **kwargs) -> "Config":
        """Load a configuration from a directory on disk."""
        _set_if_not(kwargs, "require_success", True)
        return Config(
            _ARBITER.decode_directory(pathlike, *args, **kwargs).data
        )

    @staticmethod
    def from_path(pathlike: _Pathlike, *args, **kwargs) -> "Config":
        """Load a configuration from an arbitrary path."""

        path = _normalize(pathlike)

        # Load this as a directory if it is one.
        if path.is_dir():
            return Config.from_directory(path, *args, **kwargs)

        candidates = list(
            _FileExtension.data_candidates(path, exists_only=True)
        )
        count = len(candidates)
        assert (
            count == 1
        ), f"Found {count} configurations for '{path}': {candidates}."

        # Load the data file.
        result = Config.from_file(candidates[0], *args, **kwargs)

        # Also load a directory of the stem name matches one. Load this data
        # via merging dictionaries.
        to_check = path.with_suffix("")
        if to_check.is_dir():
            result.merge(Config.from_directory(to_check).data)

        return result
