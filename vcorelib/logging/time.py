"""
A module with interfaces for time and logging integration.
"""

# built-in
from contextlib import contextmanager
from logging import INFO as _INFO
from typing import Iterator as _Iterator

# internal
from vcorelib.math.time import TIMER, LoggerType


@contextmanager
def log_time(
    log: LoggerType,
    message: str,
    *args,
    level: int = _INFO,
    reminder: bool = False,
    **kwargs,
) -> _Iterator[None]:
    """
    A simple context manager for conveniently logging time taken for a task.
    """
    with TIMER.log(
        log, message, *args, level=level, reminder=reminder, **kwargs
    ):
        yield
