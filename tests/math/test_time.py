"""
vcorelib - Test the 'math.time' module.
"""

# module under test
from vcorelib.math import (
    BILLION,
    byte_count_str,
    default_time_ns,
    nano_str,
    rate_str,
    seconds_str,
    simulated_time,
)


def test_simulated_time_basic():
    """
    Test that we can take control over the global time source as a managed
    context.
    """

    start = default_time_ns()

    with simulated_time(start_ns=0) as sim_time:
        assert default_time_ns() == 0
        sim_time.step()
        assert default_time_ns() == 1
        sim_time.step(-1)
        assert default_time_ns() == 0

        sim_time.step_s(1.0)
        assert default_time_ns() == BILLION

        sim_time.step_s(-1.0)
        assert default_time_ns() == 0

    with simulated_time(100, start_ns=0) as sim_time:
        assert default_time_ns() == 0
        sim_time.step()
        assert default_time_ns() == 100
        sim_time.step(-2)
        assert default_time_ns() == -100

    with simulated_time() as sim_time:
        assert default_time_ns() >= start

    assert default_time_ns() >= start


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


def test_rate_str_basic():
    """Test the 'rate_str' method."""

    assert rate_str(1.0) == "1 Hz (1s)"
