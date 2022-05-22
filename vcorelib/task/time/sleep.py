"""
A module implementing a task that can be used to sleep.
"""

# built-in
import asyncio

# internal
from vcorelib.task import Inbox as _Inbox
from vcorelib.task import Outbox, Task


class SleepTask(Task):
    """A task for sleeping for some duration."""

    async def run(
        self, inbox: _Inbox, outbox: Outbox, *args, **kwargs
    ) -> bool:
        """Sleep for the amount of time specified."""

        # Allow duration to be specified by keyword argument or positional.
        keyword = {**kwargs}
        duration = keyword.get("duration", args[0])

        await asyncio.sleep(duration)
        return True
