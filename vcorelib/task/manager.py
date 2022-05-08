"""
A simple task management interface.
"""

import asyncio

# built-in
from collections import defaultdict
from typing import Dict, Iterable, Set

# internal
from vcorelib.task import Task


class TaskManager:
    """
    A class for managing concurrent execution of tasks and also interfacing
    them via names.
    """

    def __init__(self) -> None:
        """Initialize this task manager."""

        self.tasks: Dict[str, Task] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.finalized: bool = False

    def register(self, task: Task, dependencies: Iterable[str] = None) -> None:
        """Register a new task and apply any requested dependencies."""

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
            await asyncio.gather(
                *[self.tasks[x].dispatch(**kwargs) for x in tasks]
            )

        asyncio.run(executor())
