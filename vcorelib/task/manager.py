"""
A simple task management interface.
"""

# built-in
from asyncio import gather
from asyncio import get_event_loop as _get_event_loop
from collections import defaultdict
from typing import Dict as _Dict
from typing import Iterable as _Iterable
from typing import List as _List
from typing import Set as _Set
from typing import Tuple as _Tuple
from typing import cast

# internal
from vcorelib.target import TargetMatch
from vcorelib.target.resolver import TargetResolver
from vcorelib.task import Task


class TaskManager:
    """
    A class for managing concurrent execution of tasks and also interfacing
    them via names.
    """

    def __init__(self, resolver: TargetResolver = None) -> None:
        """Initialize this task manager."""

        self.tasks: _Dict[str, Task] = {}
        self.dependencies: _Dict[str, _Set[str]] = defaultdict(set)
        self.finalized: bool = False
        if resolver is None:
            resolver = TargetResolver()
        self.resolver = resolver
        self.eloop = _get_event_loop()

    def register(
        self,
        task: Task,
        dependencies: _Iterable[str] = None,
        target: str = None,
    ) -> None:
        """Register a new task and apply any requested dependencies."""

        # Register this target so that it will return the provided task if
        # matched.
        if target is None:
            target = task.name
        self.resolver.register(target, task)

        self.tasks[task.name] = task
        if dependencies is None:
            dependencies = []
        self.dependencies[task.name].update(dependencies)
        self.finalized = False

    def register_to(self, target: str, dependencies: _Iterable[str]) -> None:
        """Register dependencies to a task by name."""
        self.register(self.tasks[target], dependencies)

    async def finalize(self, **kwargs) -> None:
        """Register task dependencies while the event loop is running."""

        if not self.finalized:
            for task, deps in self.dependencies.items():
                self.tasks[task].depend_on_all(
                    (self.tasks[x] for x in deps), **kwargs
                )
            self.finalized = True

    def execute(self, tasks: _Iterable[str], **kwargs) -> None:
        """Execute some set of provided tasks."""

        async def executor() -> None:
            """Wait for all of the configured tasks to complete."""
            await self.finalize(**kwargs)

            # Gather all tasks by finding matches via the target resolver.
            task_objs: _List[_Tuple[Task, TargetMatch]] = [
                (cast(Task, x.data), x.result)
                for x in self.resolver.evaluate_all(tasks)
            ]

            # Run all tasks together in the event loop.
            await gather(
                *[
                    x[0].dispatch(substitutions=x[1].substitutions, **kwargs)
                    for x in task_objs
                ]
            )

        self.eloop.run_until_complete(executor())
