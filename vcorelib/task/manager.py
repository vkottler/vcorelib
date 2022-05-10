"""
A simple task management interface.
"""

import asyncio
from collections import defaultdict

# built-in
from typing import Dict, Iterable, List, Set, Tuple, cast

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

        self.tasks: Dict[str, Task] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.finalized: bool = False
        if resolver is None:
            resolver = TargetResolver()
        self.resolver = resolver
        self.eloop = asyncio.get_event_loop()

    def register(
        self,
        task: Task,
        dependencies: Iterable[str] = None,
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

    def register_to(self, target: str, dependencies: Iterable[str]) -> None:
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

    def execute(self, tasks: Iterable[str], **kwargs) -> None:
        """Execute some set of provided tasks."""

        async def executor() -> None:
            """Wait for all of the configured tasks to complete."""
            await self.finalize(**kwargs)

            # Gather all tasks by finding matches via the target resolver.
            task_objs: List[Tuple[Task, TargetMatch]] = [
                (cast(Task, x.data), x.result)
                for x in self.resolver.evaluate_all(tasks)
            ]

            # Run all tasks together in the event loop.
            await asyncio.gather(
                *[
                    x[0].dispatch(substitutions=x[1].substitutions, **kwargs)
                    for x in task_objs
                ]
            )

        self.eloop.run_until_complete(executor())
