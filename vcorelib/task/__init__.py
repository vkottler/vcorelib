"""
A module for implementing tasks in a dependency tree.
"""

# built-in
import asyncio
from logging import Logger, getLogger
from typing import Any, Callable, Coroutine, Dict, Iterable, List

# third-party
from vcorelib.math.time import Timer, nano_str

Outbox = dict
Inbox = Dict[str, Outbox]
TaskExecute = Callable[[Inbox, Outbox], Coroutine[Any, Any, bool]]


class Task:  # pylint: disable=too-many-instance-attributes
    """A basic task interface definition."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Override this method to implement the task."""

        self.log.info(
            "inbox=%s, outbox=%s, args=%s, kwargs=%s",
            inbox,
            outbox,
            args,
            kwargs,
        )
        return True

    def create_execute(self, *args, **kwargs) -> TaskExecute:
        """Create a default execute function for this task."""

        async def wrapper(inbox: Inbox, outbox: Outbox) -> bool:
            """A default implementation for a basic task. Override this."""
            return await self.run(inbox, outbox, *args, **kwargs)

        return wrapper

    def __init__(
        self,
        name: str,
        *args,
        execute: TaskExecute = None,
        log: Logger = None,
        **kwargs
    ) -> None:
        """Initialize this task."""

        self.name = name
        self.inbox: Inbox = {}
        self.outbox: dict = {}
        self.dependencies: List[asyncio.Task] = []
        self.resolved = False

        # Metrics.
        self.times_invoked: int = 0
        self.dependency_time: int = 0
        self.execute_time: int = 0
        self.timer = Timer()

        # Get a logger if needed.
        if log is None:
            log = getLogger(name)
        self.log = log

        # Create an execute function if none was provided.
        if execute is None:
            execute = self.create_execute(*args, **kwargs)
        self.execute = execute

    def depend_on(self, task: "Task") -> None:
        """Register other tasks' output data to your input box."""

        self.inbox[task.name] = task.outbox
        self.dependencies.append(asyncio.create_task(task.dispatch()))

    def depend_on_all(self, tasks: Iterable["Task"]) -> None:
        """Register multiple dependencies."""
        for task in tasks:
            self.depend_on(task)

    async def dispatch(self) -> None:
        """Dispatch this task and return whether or not it succeeded."""

        self.times_invoked += 1
        if self.resolved:
            return

        # Wait for dependencies to finish processing.
        with self.timer.measure_ns() as token:
            for task in self.dependencies:
                await task
        self.dependency_time = self.timer.result(token)
        self.log.debug("dependencies: %s", nano_str(self.dependency_time))

        # Execute this task and don't propagate to tasks if this task failed.
        with self.timer.measure_ns() as token:
            assert await self.execute(self.inbox, self.outbox)
        self.execute_time = self.timer.result(token)
        self.log.debug("execute: %s", nano_str(self.execute_time))

        self.resolved = True
