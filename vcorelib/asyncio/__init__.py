"""
A module for working with asyncio.
"""

from __future__ import annotations

# built-in
from asyncio import AbstractEventLoop as _AbstractEventLoop
from asyncio import CancelledError as _CancelledError
from asyncio import Event as _Event
from asyncio import Task as _Task
from asyncio import all_tasks as _all_tasks
from asyncio import get_event_loop as _get_event_loop
from contextlib import suppress as _suppress
from logging import getLogger as _getLogger
from typing import Any as _Any
from typing import Awaitable as _Awaitable
from typing import Coroutine as _Coroutine
from typing import Iterable as _Iterable
from typing import List as _List
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar

# internal
from vcorelib.logging import LoggerType as _LoggerType

T = _TypeVar("T")
LOG = _getLogger(__name__)


def log_task_exception(task: _Task[_Any], logger: _LoggerType = None) -> None:
    """If a task is done and raised an exception, log it."""

    if logger is None:
        logger = LOG

    if task.done():
        with _suppress(_CancelledError):
            exc = task.exception()
            if exc is not None:
                logger.exception("Task raised exception:", exc_info=exc)


def log_exceptions(
    tasks: _Iterable[_Task[T]], logger: _LoggerType = None
) -> _List[_Task[T]]:
    """Log task exception and return the list of tasks that aren't complete."""

    for task in tasks:
        log_task_exception(task, logger=logger)
    return [x for x in tasks if not x.done()]


def shutdown_loop(
    eloop: _AbstractEventLoop, logger: _LoggerType = None
) -> None:
    """Attempt to shut down an event loop."""

    eloop.run_until_complete(eloop.shutdown_asyncgens())

    tasks = log_exceptions(_all_tasks(loop=eloop), logger=logger)
    if tasks:
        # Cancel all tasks running in the event loop.
        for task in tasks:
            task.cancel()

            # Give all tasks a chance to complete.
            with _suppress(KeyboardInterrupt, _CancelledError):
                eloop.run_until_complete(task)
                log_task_exception(task, logger=logger)


def run_handle_interrupt(
    to_run: _Awaitable[_Any], eloop: _AbstractEventLoop
) -> _Optional[_Any]:
    """
    Run a task in an event loop and gracefully handle keyboard interrupts.

    Return the result of the awaitable or None if execution was interrupted.
    """

    result = None
    try:
        result = eloop.run_until_complete(to_run)
    except KeyboardInterrupt:
        shutdown_loop(eloop)

    return result


def run_handle_stop(
    stop_sig: _Event,
    task: _Coroutine[None, None, T],
    eloop: _AbstractEventLoop = None,
) -> T:
    """
    Publish the stop signal on keyboard interrupt and wait for the task to
    complete.
    """

    if eloop is None:
        eloop = _get_event_loop()
    to_run = eloop.create_task(task)

    while True:
        try:
            return eloop.run_until_complete(to_run)
        except KeyboardInterrupt:  # pragma: nocover
            print("Keyboard interrupt.")
            stop_sig.set()
