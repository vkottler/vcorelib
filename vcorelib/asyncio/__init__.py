"""
A module for working with asyncio.
"""

# built-in
from asyncio import AbstractEventLoop as _AbstractEventLoop
from asyncio import CancelledError as _CancelledError
from asyncio import Event as _Event
from asyncio import all_tasks as _all_tasks
from asyncio import get_event_loop as _get_event_loop
from contextlib import suppress as _suppress
from typing import Any as _Any
from typing import Awaitable as _Awaitable
from typing import Coroutine as _Coroutine
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar


def shutdown_loop(eloop: _AbstractEventLoop) -> None:
    """Attempt to shut down an event loop."""

    eloop.run_until_complete(eloop.shutdown_asyncgens())

    tasks = [x for x in _all_tasks(loop=eloop) if not x.done()]
    if tasks:
        # Cancel all tasks running in the event loop.
        for task in tasks:
            task.cancel()

            # Give all tasks a chance to complete.
            with _suppress(KeyboardInterrupt, _CancelledError):
                eloop.run_until_complete(task)
                task.exception()


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


T = _TypeVar("T")


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
