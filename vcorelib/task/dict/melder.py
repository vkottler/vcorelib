"""
A task definition for melding inbox data into outbox data.
"""

# internal
from vcorelib.dict import merge
from vcorelib.task import Inbox as _Inbox
from vcorelib.task import Outbox, Task


class DictMerger(Task):
    """A class that pipes inbox data through to outbox data."""

    async def run(self, inbox: _Inbox, outbox: Outbox, *args, **_) -> bool:
        """Override this method to implement the task."""

        # Forward the foreign argument to the ouput box (provided by the
        # caller).
        merge(outbox, args[0], logger=self.log)

        # Forward all inputs to the output box.
        merge(outbox, inbox, logger=self.log)
        return True
