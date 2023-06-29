"""
Test the 'math.analysis.weighted' module.
"""

# module under test
from vcorelib.math import WeightedAverage


def test_weighted_average_basic():
    """Test basic interactions with a weighted average."""

    average = WeightedAverage()

    assert average.average() == 0.0

    average(10.0)
    average(1.0, 5.0)

    # 10 is weighted 1/6, 1 is weighted 5/6.
    expected = (10.0 / 6.0) + (1.0 * (5.0 / 6.0))

    assert average.average() == expected
