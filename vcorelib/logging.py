"""
Utilities for logging information.
"""

# built-in
from contextlib import contextmanager
from logging import INFO as _INFO
from logging import Logger
from typing import Iterator as _Iterator

# internal
from vcorelib.math.time import TIMER as _TIMER


@contextmanager
def log_time(
    log: Logger,
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
