"""
Utilities for logging information.
"""

# built-in
from contextlib import contextmanager
from logging import INFO as _INFO
from logging import getLogger as _GetLogger
from typing import Iterator as _Iterator

from vcorelib.math.time import LoggerType

# internal
from vcorelib.math.time import TIMER as _TIMER

# Re-export 'LoggerType'.
__all__ = ["LoggerType", "log_time", "LoggerMixin"]


@contextmanager
def log_time(
    log: LoggerType,
    message: str,
    *args,
    level: int = _INFO,
    **kwargs,
) -> _Iterator[None]:
    """
    A simple context manager for conveniently logging time taken for a task.
    """
    with _TIMER.log(log, message, *args, level=level, **kwargs):
        yield


class LoggerMixin:  # pylint: disable=too-few-public-methods
    """A class that provides an inheriting class a logger attribute."""

    logger: LoggerType

    def __init__(self, logger: LoggerType = None) -> None:
        """Initialize this object with logging capabilities."""
        if not hasattr(self, "logger"):
            # Set a logger for this class instance.
            if logger is None:
                logger = _GetLogger(self.__class__.__module__)
            self.logger = logger

    @contextmanager
    def log_time(
        self,
        message: str,
        *args,
        level: int = _INFO,
        **kwargs,
    ) -> _Iterator[None]:
        """A simple wrapper."""
        with log_time(self.logger, message, *args, level=level, **kwargs):
            yield
