"""
Test the 'math.analysis.rate' module.
"""

# internal
from time import sleep

# third-party
from pytest import approx

# module under test
from vcorelib.math import RateTracker


def test_rate_tracker_basic():
    """Test basic functionality of the rate tracker."""

    tracker = RateTracker()

    for _ in range(tracker.average.depth):
        tracker()
        sleep(0.001)

    assert tracker.value > 0.0
    assert tracker.min > 0.0
    assert tracker.max > 0.0

    tracker.reset()

    tracker.prev_time_ns = int(1 * 1e9)
    for i in range(tracker.average.depth * 10):
        tracker(int((i + 2) * 1e9))
        sleep(0.001)

    # Confirm that the rate tracking approaches a correct value.
    assert tracker.value == approx(1.0)
    assert tracker.min == approx(1.0)
    assert tracker.max == approx(1.0)

    tracker.reset()
    for _ in range(tracker.average.depth):
        with tracker.measure():
            sleep(0.001)
    assert tracker.value > 0.0
