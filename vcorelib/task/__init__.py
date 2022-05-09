"""
A module for implementing tasks in a dependency tree.
"""

# built-in
import asyncio
from collections import UserDict
from io import StringIO
from logging import Logger, getLogger
from typing import Any, Callable, Coroutine, Dict, Iterable, List, Set

# internal
from vcorelib.math.time import Timer, nano_str

Outbox = dict


class Inbox(UserDict):
    """A simple dictionary with a separate member for private data."""

    def __init__(self, initialdata: Dict[str, Outbox] = None) -> None:
        """Initialize this inbox."""
        super().__init__(initialdata)
        self.private: dict = {}


TaskExecute = Callable[[Inbox, Outbox], Coroutine[Any, Any, bool]]


class Task:  # pylint: disable=too-many-instance-attributes
    """A basic task interface definition."""

    def __init__(
        self,
        name: str,
        *args,
        execute: TaskExecute = None,
        log: Logger = None,
        timer: Timer = None,
        **kwargs
    ) -> None:
        """Initialize this task."""

        self.name = name
        self.inbox: Inbox = Inbox()
        self.outbox: dict = {}
        self.dependencies: List[asyncio.Task] = []
        self.resolved = False
        self.literals_resolved: Set[str] = set()

        # Metrics.
        self.times_invoked: int = 0
        self.dependency_time: int = 0
        self.execute_time: int = 0
        if timer is None:
            timer = Timer()
        self.timer = timer

        # Get a logger if needed.
        if log is None:
            log = getLogger(name)
        self.log = log

        # Create an execute function if none was provided.
        if execute is None:
            execute = self.create_execute(*args, **kwargs)
        self.execute = execute

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

    def __str__(self) -> str:
        """Convert this task to a string."""

        with StringIO() as stream:
            stream.write(self.name)
            if self.dynamic:
                stream.write(" (")
                stream.write(self.inbox.private["literal"])
                stream.write(")")
            return stream.getvalue()

    def create_execute(self, *args, **kwargs) -> TaskExecute:
        """Create a default execute function for this task."""

        async def wrapper(inbox: Inbox, outbox: Outbox) -> bool:
            """A default implementation for a basic task. Override this."""
            return await self.run(inbox, outbox, *args, **kwargs)

        return wrapper

    def depend_on(self, task: "Task", **kwargs) -> None:
        """Register other tasks' output data to your input box."""

        self.inbox[task.name] = task.outbox
        self.dependencies.append(
            asyncio.create_task(task.dispatch(self, **kwargs))
        )

    def depend_on_all(self, tasks: Iterable["Task"], **kwargs) -> None:
        """Register multiple dependencies."""
        for task in tasks:
            self.depend_on(task, **kwargs)

    @property
    def dynamic(self) -> bool:
        """Determine if this is a dynamic task or not."""
        return self.inbox.private.get("substitutions") is not None

    async def dispatch(
        self,
        caller: "Task" = None,
        init_only: bool = False,
    ) -> None:
        """Dispatch this task and return whether or not it succeeded."""

        self.times_invoked += 1

        # Pass information about target resolution, if we're a dynamic target,
        # to any dependencies.
        if self.dynamic:
            self.outbox["substitutions"] = self.inbox.private["substitutions"]
            literal = self.inbox.private["literal"]
            self.outbox["literal"] = literal
            self.log = getLogger(literal)

            if literal in self.literals_resolved:
                return
        elif self.resolved:
            return

        if caller is not None:
            self.log.debug("triggered by '%s'", caller)

        # Wait for dependencies to finish processing.
        with self.timer.measure_ns() as token:
            await asyncio.gather(*self.dependencies)
        self.dependency_time = self.timer.result(token)
        self.log.debug("dependencies: %s", nano_str(self.dependency_time))

        # Allow a dry-run pass get only this far (before executing).
        if init_only:
            return

        with self.timer.measure_ns() as token:
            # Execute this task and don't propagate to tasks if this task
            # failed.
            assert await self.execute(self.inbox, self.outbox)

        self.execute_time = self.timer.result(token)
        self.log.debug("execute: %s", nano_str(self.execute_time))

        # Track that this task was resolved.
        literal = self.inbox.private.get("literal")
        if literal is not None:
            self.literals_resolved.add(literal)
        self.resolved = True
