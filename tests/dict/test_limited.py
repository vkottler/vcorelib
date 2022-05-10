"""
Test the 'limited' method from the 'dict' module.
"""

# module under test
from vcorelib.dict import limited


def test_limited_basic():
    """Test basic functionality of the limited method."""

    data = {"a": 1}
    with limited(data, "a", 2):
        assert data["a"] == 2
    assert data["a"] == 1

    with limited(data, "b"):
        assert "b" not in data
