"""
A module for interacting with JSON schemas.
"""

# built-in
from logging import getLogger as _getLogger
from typing import Any as _Any
from typing import Type as _Type
from urllib.parse import urlparse as _urlparse

# third-party
from fastjsonschema import JsonSchemaException as _JsonSchemaException
from fastjsonschema import compile as _compile

# internal
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import find_file
from vcorelib.schemas.base import Schema as _Schema
from vcorelib.schemas.base import SchemaMap as _SchemaMap
from vcorelib.schemas.base import SchemaValidationError

LOG = _getLogger(__name__)


def package_handler(uri: str) -> _JsonObject:
    """Load data from a package."""

    parsed = _urlparse(uri)
    assert parsed.scheme == "package"

    path = find_file(parsed.path[1:], package=parsed.hostname, logger=LOG)
    assert path is not None, path
    return _ARBITER.decode(path, require_success=True).data


class JsonSchema(_Schema):
    """
    An object wrapper for: https://horejsek.github.io/python-fastjsonschema/.

    See also: https://json-schema.org/.
    """

    def __init__(self, data: _JsonObject) -> None:
        """Initialize this schema."""
        super().__init__(data)
        self.validator = _compile(data, handlers={"package": package_handler})

    def __call__(self, data: _Any) -> _Any:
        """Validate input data and return the result."""
        try:
            return self.validator(data)
        except _JsonSchemaException as exc:
            raise SchemaValidationError(exc) from exc


class JsonSchemaMap(_SchemaMap):
    """A class for managing multiple schema objects."""

    @classmethod
    def kind(cls) -> _Type[JsonSchema]:
        """Implement this to determine the concrete schema type."""
        return JsonSchema
