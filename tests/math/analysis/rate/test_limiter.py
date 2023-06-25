"""
Test the 'math.analysis.rate.limiter' module.
"""

# third-party
from pytest import approx

# module under test
from vcorelib.math import RateLimiter


def test_rate_limiter_basic():
    """Test that the rate-limiter works correctly."""

    second = int(1e9)

    lim = RateLimiter(second)

    curr = second
    lim(curr)

    for _ in range(100):
        curr += second
        assert lim(curr, lambda: None)

    assert not lim(curr)

    assert lim.rate_hz == approx(1.0)

    assert lim()
