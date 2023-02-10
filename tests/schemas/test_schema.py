"""
Test the 'schemas' module.
"""

# third-party
from pytest import raises

# internal
from tests.resources import get_test_schemas

# module under test
from vcorelib.dict.codec import BasicDictCodec
from vcorelib.schemas import CerberusSchema, CerberusSchemaMap
from vcorelib.schemas.base import SchemaValidationError


def test_json_schema_map_basic():
    """Test basic interactions iwth a JSON-schema map."""

    schemas = get_test_schemas()
    assert "A" in schemas and "B" in schemas

    # Test that schema validation works.
    assert schemas["A"]("hello") == "hello"
    assert schemas["B"]({}) == {"a": 42}

    # Verify that we raise an exception.
    with raises(SchemaValidationError):
        schemas["A"](5)


class A(BasicDictCodec):  # pylint: disable=invalid-name
    """A test class."""

    default_schemas = get_test_schemas()


class B(A):  # pylint: disable=invalid-name
    """A test class."""


def test_json_schema_mixin_basic():
    """Test that the class mixin for JSON schemas works."""

    assert B.create().data == {"a": 42}


def test_json_schema_references():
    """Test that we can resolve schema references."""

    class C(B):  # pylint: disable=invalid-name
        """A class with an underlying schema."""

    result = C.create({"a": "hello", "b": {}})
    assert result.data["a"] == "hello"
    assert result.data["b"]["a"] == 42  # type: ignore


def test_cerberus_schema_basic():
    """Test basic functionality of cerberus schemas."""

    schema = CerberusSchema({"name": {"type": "string"}})
    assert schema({"name": "test"}) == {"name": "test"}

    # Verify that we raise an exception.
    with raises(SchemaValidationError):
        assert schema({"name": 5})

    assert CerberusSchemaMap.kind() is CerberusSchema
