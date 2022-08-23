"""
A module for working with various schema enforcement implementations.
"""

# built-in
from typing import Any as _Any
from typing import Type as _Type

# third-party
from cerberus import Validator as _Validator
from fastjsonschema import JsonSchemaException as _JsonSchemaException
from fastjsonschema import compile as _compile

# internal
from vcorelib.schemas.base import Schema as _Schema
from vcorelib.schemas.base import SchemaMap as _SchemaMap


class SchemaValidationError(Exception):
    """An exception type for schema errors."""


class JsonSchema(_Schema):
    """
    An object wrapper for: https://horejsek.github.io/python-fastjsonschema/.

    See also: https://json-schema.org/.
    """

    def __init__(self, data: dict, **kwargs) -> None:
        """Initialize this schema."""
        super().__init__(data)
        self.validator = _compile(data)

    def __call__(self, data: _Any) -> _Any:
        """Validate input data and return the result."""
        try:
            return self.validator(data)
        except _JsonSchemaException as exc:
            raise SchemaValidationError(exc) from exc


class JsonSchemaMap(_SchemaMap):
    """A class for managing multiple schema objects."""

    @classmethod
    def kind(cls) -> _Type[_Schema]:
        """Implement this to determine the concrete schema type."""
        return JsonSchema


class CerberusSchema(_Schema):
    """An object wrapper for: https://docs.python-cerberus.org/en/stable/."""

    def __init__(self, data: dict, **kwargs) -> None:
        """Initialize this schema."""
        super().__init__(data)
        self.validator = _Validator(data, **kwargs)

    def __call__(self, data: _Any) -> _Any:
        """Validate input data and return the result."""

        # Normalize the data first.
        data = self.validator.normalized(data)
        if data is not None:
            # Run validation rules.
            if self.validator.validate(data, normalize=False):
                return data

        # Raise error(s).
        raise SchemaValidationError(self.validator.errors)


class CerberusSchemaMap(_SchemaMap):
    """A class for managing multiple schema objects."""

    @classmethod
    def kind(cls) -> _Type[_Schema]:
        """Implement this to determine the concrete schema type."""
        return CerberusSchema
