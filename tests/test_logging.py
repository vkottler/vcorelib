"""
vcorelib - Test the 'logging' module.
"""

# internal
from logging import getLogger

# module under test
from vcorelib.logging import LoggerMixin, log_time


def test_log_time_basic():
    """Test that log_time works in a simple scenario."""

    log = getLogger(__name__)
    with log_time(log, "Example"):
        for _ in range(100):
            pass


def test_logger_mixin_basic():
    """Test basic functionality of the logger mixin."""

    class LoggerMixinTest(
        LoggerMixin
    ):  # pylint: disable=too-few-public-methods
        """A test class."""

    inst = LoggerMixinTest()
    inst.logger.info("This is a test, %d %d %d.", 1, 2, 3)

    with inst.log_time("Hello, %s! %d", "world", 5):
        for _ in range(100):
            pass
