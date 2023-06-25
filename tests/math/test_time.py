"""
vcorelib - Test the 'math.time' module.
"""

# module under test
from vcorelib.math import byte_count_str, nano_str, seconds_str


def test_nano_str_basic():
    """Test that the 'nano_str' method produces the correct results."""

    val = 1
    assert nano_str(val) == "1n"
    val = val * 1000 + 1
    assert nano_str(val) == "1.001u"
    val *= 1000
    assert nano_str(val) == "1.001m"
    val *= 1000
    assert nano_str(val) == "1.001"
    val *= 1000
    assert nano_str(val) == "1001"

    assert nano_str(val, max_prefix=4) == "1.001k"
    assert nano_str(val * 1000, max_prefix=5) == "1.001M"

    # Test when the value is time.
    assert nano_str(val, True) == "16m 41"


def test_seconds_str_basic():
    """Test that the 'seconds_str' method produces the correct results."""

    assert seconds_str(60) == ("1m", 0)
    assert seconds_str(61) == ("1m", 1)
    assert seconds_str(3600) == ("1h 0m", 0)
    assert seconds_str(3661) == ("1h 1m", 1)


def test_byte_count_str():
    """Test that the 'byte_count_str' method produces the correct results."""

    assert byte_count_str(0) == "0 B"
    assert byte_count_str(1024) == "1 KiB"
    assert byte_count_str(1536) == "1.500 KiB"
