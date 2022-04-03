"""
Utilities for logging information.
"""

# built-in
from contextlib import contextmanager
from logging import INFO as _INFO
from logging import Logger
from time import perf_counter_ns as _perf_counter_ns
from typing import Iterator as _Iterator

# internal
from vcorelib.math.time import nano_str


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

    start = _perf_counter_ns()
    yield
    time_ns = _perf_counter_ns() - start

    # Log the duration spent yielded.
    log.log(
        level,
        message + " completed in %ss.",
        *args,
        nano_str(time_ns, True),
        **kwargs,
    )
