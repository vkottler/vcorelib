"""
A module for implementing schema-validated classes.
"""

# internal
from vcorelib.schemas.base import Schema as _Schema
from vcorelib.schemas.base import SchemaMap as _SchemaMap


class SchemaMixin:
    """
    A class that allows inheriting classes to validate an attribute with a
    schema.
    """

    schema: _Schema

    def __init__(self, schemas: _SchemaMap, valid_attr: str = "data") -> None:
        """Initialize this object instance by performing schema validation."""

        # Don't double initialize.
        if not hasattr(self, "schema"):
            # Allow the name of the schema to be overridden if necessary.
            schema = self.schema_name()
            assert schema in schemas, f"No schema for '{schema}'!"
            self.schema = schemas[schema]

            # Perform validation.
            self.validate(valid_attr=valid_attr)

    @classmethod
    def schema_name(cls) -> str:
        """A default name for this class's schema."""
        return cls.__name__

    def validate(self, valid_attr: str = "data") -> None:
        """Validate an instance attribute based on this instance's schema."""

        # Ensure that this object has the specified attribute.
        assert hasattr(
            self, valid_attr
        ), f"Object doesn't have attribute '{valid_attr}' to validate!"

        # Validate object data. Re-assign the result.
        setattr(self, valid_attr, self.schema(getattr(self, valid_attr)))
