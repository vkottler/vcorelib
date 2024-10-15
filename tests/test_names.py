"""
Test the 'names' module.
"""

# module under test
from vcorelib.names import (
    import_str_and_item,
    name_search,
    obj_class_to_snake,
    to_snake,
)


def test_snake_basic():
    """Test basic scenarios for converting names to snake-case."""

    class SampleClass:  # pylint: disable=too-few-public-methods
        """A sample class."""

    assert obj_class_to_snake(SampleClass()) == "sample_class"

    assert to_snake("my-project") == "my_project"
    assert to_snake("my-project", lower_dashes=False) == "my-project"
    assert to_snake("MyProject") == "my_project"


def test_name_search_basic():
    """Test basic name searching scenarios."""

    assert "test" in name_search({"test"}, "test")
    assert "test1" in name_search({"test1"}, "test")
    assert not list(name_search({"test1"}, "test", exact=True))


def test_import_str_and_item_basic():
    """Test basic string manipulation."""

    assert import_str_and_item("a.b.c") == ("a.b", "c")
