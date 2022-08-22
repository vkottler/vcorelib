"""
Test the 'schemas' module.
"""

# built-in
from os.path import join

# module under test
from vcorelib.schemas import JsonSchemaMap
from vcorelib.schemas.mixins import JsonSchemaMixin


def test_json_schema_map_basic():
    """Test basic interactions iwth a JSON-schema map."""

    schemas = JsonSchemaMap.from_package(
        "tests", package_subdir=join("data", "valid")
    )
    assert "A" in schemas and "B" in schemas

    # Test that schema validation works.
    assert schemas["A"]("hello") == "hello"
    assert schemas["B"]({}) == {"a": 42}


def test_json_schema_mixin_basic():
    """Test that the class mixin for JSON schemas works."""

    schemas = JsonSchemaMap.from_package(
        "tests", package_subdir=join("data", "valid")
    )

    class A(
        JsonSchemaMixin
    ):  # pylint: disable=too-few-public-methods,invalid-name
        """A test class."""

        def __init__(self) -> None:
            self.data = "hello"
            super().__init__(schemas)

    class B(
        JsonSchemaMixin
    ):  # pylint: disable=too-few-public-methods,invalid-name
        """A test class."""

        def __init__(self) -> None:
            self.data: dict = {}
            super().__init__(schemas)

    assert A().data == "hello"
    assert B().data == {"a": 42}
