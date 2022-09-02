"""
A module for working with asyncio.
"""

# built-in
from asyncio import AbstractEventLoop as _AbstractEventLoop
from asyncio import all_tasks as _all_tasks
from contextlib import suppress as _suppress
from typing import Awaitable as _Awaitable


def run_handle_interrupt(
    to_run: _Awaitable, eloop: _AbstractEventLoop
) -> None:
    """
    Run a task in an event loop and gracefully handle keyboard interrupts.
    """

    try:
        eloop.run_until_complete(to_run)
    except KeyboardInterrupt:
        tasks = _all_tasks(loop=eloop)

        # Cancel all tasks running in the event loop.
        for task in tasks:
            if not task.done():
                task.cancel()

                # Wait for the task to complete.
                with _suppress(KeyboardInterrupt):
                    eloop.run_until_complete(task)
