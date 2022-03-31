"""
vcorelib - Utilities for logging information.
"""

# built-in
from contextlib import contextmanager
import logging
from time import perf_counter_ns
from typing import Iterator

# internal
from vcorelib.math.time import nano_str


@contextmanager
def log_time(
    log: logging.Logger,
    message: str,
    *args,
    level: int = logging.INFO,
    **kwargs,
) -> Iterator[None]:
    """
    A simple context manager for conveniently logging time taken for a task.
    """

    start = perf_counter_ns()
    yield
    time_ns = perf_counter_ns() - start

    # Log the duration spent yielded.
    log.log(
        level,
        message + " completed in %ss.",
        *args,
        nano_str(time_ns, True),
        **kwargs,
    )
