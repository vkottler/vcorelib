"""
A module for working with various schema enforcement implementations.
"""

# built-in
from typing import Any as _Any
from typing import Optional as _Optional
from typing import Type as _Type

# third-party
from cerberus import Validator as _Validator

# internal
from vcorelib import PKG_NAME
from vcorelib.dict.codec import DictCodec as _DictCodec
from vcorelib.io import DEFAULT_INCLUDES_KEY
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.schemas.base import Schema as _Schema
from vcorelib.schemas.base import SchemaMap as _SchemaMap
from vcorelib.schemas.base import SchemaValidationError
from vcorelib.schemas.json import JsonSchemaMap as _JsonSchemaMap


class CerberusSchema(_Schema):
    """An object wrapper for: https://docs.python-cerberus.org/en/stable/."""

    def __init__(self, data: _JsonObject, **kwargs) -> None:
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
    def kind(cls) -> _Type[CerberusSchema]:
        """Implement this to determine the concrete schema type."""
        return CerberusSchema


class VcorelibDictCodec(_DictCodec):
    """
    A simple wrapper for package classes that want to implement DictCodec.
    """

    default_schemas: _Optional[_SchemaMap] = _JsonSchemaMap.from_package(
        PKG_NAME,
        includes_key=DEFAULT_INCLUDES_KEY,
    )
