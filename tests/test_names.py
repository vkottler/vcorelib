"""
Test the 'names' module.
"""

# module under test
from vcorelib.names import obj_class_to_snake, to_snake


def test_snake_basic():
    """Test basic scenarios for converting names to snake-case."""

    class SampleClass:  # pylint: disable=too-few-public-methods
        """A sample class."""

    assert obj_class_to_snake(SampleClass()) == "sample_class"

    assert to_snake("my-project") == "my_project"
    assert to_snake("my-project", lower_dashes=False) == "my-project"
    assert to_snake("MyProject") == "my_project"
