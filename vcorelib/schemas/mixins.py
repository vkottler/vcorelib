"""
A module for implementing schema-validated classes.
"""

# internal
from vcorelib.schemas import JsonSchema as _JsonSchema
from vcorelib.schemas import JsonSchemaMap as _JsonSchemaMap


class JsonSchemaMixin:  # pylint: disable=too-few-public-methods
    """
    A class that allows inheriting classes to validate an attribute with a
    schema.
    """

    schema: _JsonSchema

    def __init__(
        self, schemas: _JsonSchemaMap, valid_attr: str = "data"
    ) -> None:
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
