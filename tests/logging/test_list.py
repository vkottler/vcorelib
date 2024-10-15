"""
Test the 'logging.list' module.
"""

# built-in
from logging import getLogger

# module under test
from vcorelib.logging import ListLogger


def test_list_logger_basic():
    """Test basic interactions with a list logger."""

    handler = ListLogger.create()
    assert not handler
    assert not handler.drain_str()
    assert not handler.drain()

    logger = getLogger(__name__)
    logger.addHandler(handler)

    logger.info("test")

    assert handler
    assert handler.drain_str()
