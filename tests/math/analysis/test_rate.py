"""
Test the 'math.analysis.rate' module.
"""

# third-party
from pytest import approx

# module under test
from vcorelib.math.analysis.rate import RateTracker


def test_rate_tracker_basic():
    """Test basic functionality of the rate tracker."""

    tracker = RateTracker()

    for _ in range(1000):
        tracker()

    assert tracker.value > 0.0
    assert tracker.min > 0.0
    assert tracker.max > 0.0

    tracker.reset()

    for i in range(tracker.average.depth * 10):
        tracker(i * 10e9)

    # Confirm that the rate tracking approaches a correct value.
    assert tracker.value == approx(1.0)
    assert tracker.min == approx(1.0)
    assert tracker.max == approx(1.0)
