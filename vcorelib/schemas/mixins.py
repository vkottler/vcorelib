"""
A module for implementing schema-validated classes.
"""

# internal
from vcorelib.schemas.base import Schema as _Schema
from vcorelib.schemas.base import SchemaMap as _SchemaMap


class SchemaMixin:  # pylint: disable=too-few-public-methods
    """
    A class that allows inheriting classes to validate an attribute with a
    schema.
    """

    schema: _Schema

    def __init__(self, schemas: _SchemaMap, valid_attr: str = "data") -> None:
        """Initialize this object instance by performing schema validation."""

        # Don't double initialize.
        if not hasattr(self, "schema"):
            schema = self.__class__.__name__
            assert schema in schemas, f"No schema for '{schema}'!"
            self.schema = schemas[schema]

            # Ensure that this object has the specified attribute.
            assert hasattr(
                self, valid_attr
            ), f"Object doesn't have attribute '{valid_attr}' to validate!"

            # Validate object data. Re-assign the result.
            setattr(self, valid_attr, self.schema(getattr(self, valid_attr)))
