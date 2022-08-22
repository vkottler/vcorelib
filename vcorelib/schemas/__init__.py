"""
A module for working with schema enforcement.
"""

# built-in
from collections import UserDict
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Iterator as _Iterator
from typing import Tuple as _Tuple

# third-party
from fastjsonschema import compile as _compile

# internal
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import get_file_name as _get_file_name
from vcorelib.paths import normalize as _normalize
from vcorelib.paths import resource as _resource


class JsonSchema:
    """
    An object wrapper for: https://horejsek.github.io/python-fastjsonschema/.
    """

    def __init__(self, data: dict) -> None:
        """Initialize this schema."""
        self.validator = _compile(data)

    def __call__(self, data: _Any) -> _Any:
        """Validate input data and return the result."""
        return self.validator(data)

    @staticmethod
    def from_path(path: _Pathlike, **kwargs) -> "JsonSchema":
        """Load a schema from a data file on disk."""
        return JsonSchema(
            _ARBITER.decode(path, require_success=True, **kwargs).data
        )


class JsonSchemaMap(UserDict):
    """A class for managing multiple schema objects."""

    data: _Dict[str, JsonSchema]

    def load_file(self, path: _Pathlike, **kwargs) -> _Tuple[str, JsonSchema]:
        """Load a schema file into the map."""

        path = _normalize(path)
        name = _get_file_name(path)
        assert name not in self.data, f"Duplicate schema '{name}'!"
        self.data[name] = JsonSchema.from_path(path, **kwargs)
        return name, self.data[name]

    def load_directory(
        self, path: _Pathlike, **kwargs
    ) -> _Iterator[_Tuple[str, JsonSchema]]:
        """Load a directory of schema files into the map."""

        path = _normalize(path)
        assert path.is_dir(), f"'{path}' isn't a directory!"
        for item in path.iterdir():
            yield self.load_file(item, **kwargs)

    def load_package(
        self, package: str, path: _Pathlike = "schemas", **kwargs
    ) -> _Iterator[_Tuple[str, JsonSchema]]:
        """Load schemas from package data."""

        path = _resource(path, package=package, **kwargs)
        assert (
            path is not None and path.is_dir()
        ), f"Can't find schema directory for package '{package}'!"

        yield from self.load_directory(path)

    @staticmethod
    def from_package(
        package: str, path: _Pathlike = "schemas", **kwargs
    ) -> "JsonSchemaMap":
        """Create a new JSON-schema map from package data."""

        result = JsonSchemaMap()
        list(result.load_package(package, path=path, **kwargs))
        return result
