"""
A module for working with asyncio.
"""

# built-in
from asyncio import AbstractEventLoop as _AbstractEventLoop
from asyncio import all_tasks as _all_tasks
from asyncio import gather as _gather
from contextlib import suppress as _suppress
from typing import Any as _Any
from typing import Awaitable as _Awaitable
from typing import Optional as _Optional


def run_handle_interrupt(
    to_run: _Awaitable, eloop: _AbstractEventLoop
) -> _Optional[_Any]:
    """
    Run a task in an event loop and gracefully handle keyboard interrupts.

    Return the result of the awaitable or None if execution was interrupted.
    """

    result = None
    try:
        result = eloop.run_until_complete(to_run)
    except KeyboardInterrupt:
        tasks = [x for x in _all_tasks(loop=eloop) if not x.done()]

        # Cancel all tasks running in the event loop.
        for task in tasks:
            task.cancel()

        # Wait for the task to complete.
        with _suppress(KeyboardInterrupt):
            eloop.run_until_complete(_gather(*tasks))

    return result
