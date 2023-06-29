"""
A module for logging time-related events.
"""

# built-in
from contextlib import contextmanager
from logging import INFO as _INFO
from typing import Iterator as _Iterator

from vcorelib.math.time import LoggerType as _LoggerType

# internal
from vcorelib.math.time import TIMER as _TIMER


@contextmanager
def log_time(
    log: _LoggerType,
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
