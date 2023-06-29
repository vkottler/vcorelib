"""
A module for logging mixins for classes.
"""

# built-in
from contextlib import contextmanager
from logging import INFO as _INFO
from logging import getLogger as _GetLogger
from typing import Iterator as _Iterator

# internal
from vcorelib.logging.time import log_time as _log_time
from vcorelib.math.time import LoggerType as _LoggerType


class LoggerMixin:  # pylint: disable=too-few-public-methods
    """A class that provides an inheriting class a logger attribute."""

    logger: _LoggerType

    def __init__(self, logger: _LoggerType = None) -> None:
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
        with _log_time(self.logger, message, *args, level=level, **kwargs):
            yield
