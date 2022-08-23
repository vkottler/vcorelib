"""
Test the 'schemas' module.
"""

# built-in
from os.path import join

# third-party
from pytest import raises

# module under test
from vcorelib.schemas import (
    CerberusSchema,
    CerberusSchemaMap,
    JsonSchemaMap,
    SchemaValidationError,
)
from vcorelib.schemas.mixins import SchemaMixin


def test_json_schema_map_basic():
    """Test basic interactions iwth a JSON-schema map."""

    schemas = JsonSchemaMap.from_package(
        "tests", package_subdir=join("data", "valid")
    )
    assert "A" in schemas and "B" in schemas

    # Test that schema validation works.
    assert schemas["A"]("hello") == "hello"
    assert schemas["B"]({}) == {"a": 42}

    # Verify that we raise an exception.
    with raises(SchemaValidationError):
        schemas["A"](5)


def test_json_schema_mixin_basic():
    """Test that the class mixin for JSON schemas works."""

    schemas = JsonSchemaMap.from_package(
        "tests", package_subdir=join("data", "valid")
    )

    class A(
        SchemaMixin
    ):  # pylint: disable=too-few-public-methods,invalid-name
        """A test class."""

        def __init__(self) -> None:
            self.data = "hello"
            super().__init__(schemas)

    class B(
        SchemaMixin
    ):  # pylint: disable=too-few-public-methods,invalid-name
        """A test class."""

        def __init__(self) -> None:
            self.data: dict = {}
            super().__init__(schemas)

    assert A().data == "hello"
    assert B().data == {"a": 42}


def test_cerberus_schema_basic():
    """Test basic functionality of cerberus schemas."""

    schema = CerberusSchema({"name": {"type": "string"}})
    assert schema({"name": "test"}) == {"name": "test"}

    # Verify that we raise an exception.
    with raises(SchemaValidationError):
        assert schema({"name": 5})

    assert CerberusSchemaMap.kind() is CerberusSchema
