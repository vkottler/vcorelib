"""
A simple task management interface.
"""

# built-in
import asyncio
from typing import Dict, Iterable, List

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
        self.dependencies: Dict[str, List[str]] = {}
        self.finalized: bool = False

    def register(self, task: Task, dependencies: Iterable[str] = None) -> None:
        """Register a new task and apply any requested dependencies."""

        self.tasks[task.name] = task
        if dependencies is None:
            dependencies = []
        self.dependencies[task.name] = list(dependencies)

    async def finalize(self) -> None:
        """Register task dependencies while the event loop is running."""

        if not self.finalized:
            for task, deps in self.dependencies.items():
                self.tasks[task].depend_on_all(self.tasks[x] for x in deps)
            self.finalized = True

    def execute(self, tasks: Iterable[str]) -> None:
        """Execute some set of provided tasks."""

        async def executor() -> None:
            """Wait for all of the configured tasks to complete."""
            await self.finalize()
            await asyncio.gather(*[self.tasks[x].dispatch() for x in tasks])

        asyncio.run(executor())
