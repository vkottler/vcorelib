"""
Test the 'math.analysis.average' module.
"""

# third-party
from pytest import approx

# module under test
from vcorelib.math import MovingAverage


def test_moving_average_basic():
    """Test basic functionality of the moving average."""

    average = MovingAverage(10)
    assert not average.saturated

    assert average(10.0) == approx(1.0)
    assert average(10.0) == approx(2.0)
    assert average(10.0) == approx(3.0)
    assert average(10.0) == approx(4.0)
    assert average(10.0) == approx(5.0)
    assert average(10.0) == approx(6.0)
    assert average(10.0) == approx(7.0)
    assert average(10.0) == approx(8.0)
    assert average(10.0) == approx(9.0)
    assert not average.saturated

    assert average(10.0) == approx(10.0)
    assert average.saturated

    assert average(0.0) == approx(9.0)
    average.resize(100)
    assert average(100.0) == approx(1.0)
