"""
A module for implementing tasks in a dependency tree.
"""

# built-in
import asyncio
from logging import Logger, getLogger
from typing import Any as _Any
from typing import Callable as _Callable
from typing import Coroutine as _Coroutine
from typing import Dict as _Dict
from typing import Iterable as _Iterable
from typing import Set as _Set

# internal
from vcorelib.dict import merge_dicts
from vcorelib.math.time import Timer, nano_str
from vcorelib.target import Substitutions, Target

Outbox = dict
Inbox = _Dict[str, Outbox]
TaskExecute = _Callable[[Inbox, Outbox], _Coroutine[_Any, _Any, bool]]
TaskGenerator = _Callable[..., asyncio.Task]


class Task:  # pylint: disable=too-many-instance-attributes
    """A basic task interface definition."""

    stages = ["run_enter", "run", "run_exit"]

    def __init__(
        self,
        name: str,
        *args,
        execute: TaskExecute = None,
        log: Logger = None,
        timer: Timer = None,
        target: Target = None,
        **kwargs,
    ) -> None:
        """Initialize this task."""

        self.name = name
        self.inbox: Inbox = {}
        self.outbox: dict = {}
        self.dependencies: _Dict[Target, TaskGenerator] = {}
        self._resolved = False
        self.literals: _Set[str] = set()

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

        # Create a target if one wasn't provided.
        if target is None:
            target = Target(self.name)
        self.target: Target = target

    def __str__(self) -> str:
        """Convert this task into a string."""
        return self.name

    def resolved(self, substitutions: Substitutions = None) -> bool:
        """Override this in a derived task to implement more complex logic."""

        # Only a literal target has a boolean resolved state.
        if self.target.literal:
            return self._resolved

        # This task is only resolved if the compiled literal appears in the
        # completed set.
        assert substitutions is not None
        return self.target.compile(substitutions) in self.literals

    def resolve(self, substitutions: Substitutions = None) -> None:
        """Mark this task resolved."""

        # A literal target only needs to be resovled once.
        if self.target.literal:
            self._resolved = True
            return

        # A non-literal task must have valid substitutions.
        assert substitutions is not None
        self.literals.add(self.target.compile(substitutions))

    async def run_enter(
        self, _inbox: Inbox, _outbox: Outbox, *_args, **_kwargs
    ) -> bool:
        """A default enter method."""
        assert self
        return True

    async def run_exit(
        self, _inbox: Inbox, _outbox: Outbox, *_args, **_kwargs
    ) -> bool:
        """A default exit method."""
        assert self
        return True

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

        async def wrapper(
            inbox: Inbox, outbox: Outbox, **substitutions
        ) -> bool:
            """A default implementation for a basic task. Override this."""

            merged = merge_dicts([{}, kwargs, substitutions], logger=self.log)

            # Run through all of the stages.
            result = True
            for stage in self.stages:
                if result:
                    result = await getattr(self, stage)(
                        inbox, outbox, *args, **merged
                    )
            return result

        return wrapper

    def depend_on(self, task: "Task", **kwargs) -> bool:
        """
        Register other tasks' output data to your input box. Return true
        if a new dependency was added.
        """

        added = False
        if task.target not in self.dependencies:

            def task_factory(**substitutions) -> asyncio.Task:
                """
                Create a task while injecting additional keyword arguments.
                """
                return asyncio.create_task(
                    task.dispatch(
                        self,
                        **merge_dicts(
                            [{}, kwargs, substitutions], logger=self.log
                        ),
                    )
                )

            self.inbox[task.name] = task.outbox
            self.dependencies[task.target] = task_factory
            added = True

        return added

    def depend_on_all(self, tasks: _Iterable["Task"], **kwargs) -> int:
        """
        Register multiple dependencies. Return the number of dependencies
        added.
        """

        added_count = 0
        for task in tasks:
            added_count += int(self.depend_on(task, **kwargs))
        return added_count

    async def resolve_dependencies(self, **substitutions) -> None:
        """
        A default dependency resolver for tasks. Note that the default
        dependency resolver cannot propagate current-task substitutions to
        its dependencies as they've already been explicitly registered.
        """
        await asyncio.gather(
            *[x(**substitutions) for x in self.dependencies.values()]
        )

    async def dispatch(
        self,
        caller: "Task" = None,
        init_only: bool = False,
        substitutions: Substitutions = None,
        **kwargs,
    ) -> None:
        """Dispatch this task and return whether or not it succeeded."""

        self.times_invoked += 1

        if substitutions is None:
            substitutions = {}

        # Merge substitutions in with other command-line arguments.
        merged = merge_dicts([{}, kwargs, substitutions], logger=self.log)

        # Return early if this task has already been executed.
        if self.resolved(merged):
            return

        # Reset the outbox for this execution. Don't re-assign it or it will
        # lose its association with anything depending on it.
        for key in list(self.outbox.keys()):
            self.outbox.pop(key)

        if substitutions is not None:
            self.log.debug("substitutions: '%s'", merged)

        if caller is not None:
            self.log.debug("triggered by '%s'", caller)

        # Wait for dependencies to finish processing.
        with self.timer.measure_ns() as token:
            await self.resolve_dependencies(**merged)
        self.dependency_time = self.timer.result(token)
        self.log.debug("dependencies: %s", nano_str(self.dependency_time))

        # Allow a dry-run pass get only this far (before executing).
        if init_only:
            return

        with self.timer.measure_ns() as token:
            # Execute this task and don't propagate to tasks if this task
            # failed.
            assert await self.execute(self.inbox, self.outbox, **merged)
        self.execute_time = self.timer.result(token)
        self.log.debug("execute: %s", nano_str(self.execute_time))

        # Track that this task was resolved.
        self.resolve(merged)
