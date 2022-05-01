"""
vcorelib - Test the 'log' module.
"""

# internal
from logging import getLogger

# module under test
from vcorelib.log import log_time


def test_log_time_basic():
    """Test that log_time works in a simple scenario."""

    log = getLogger(__name__)
    with log_time(log, "Example"):
        for _ in range(100):
            pass
