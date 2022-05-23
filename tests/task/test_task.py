"""
Test the 'task' module.
"""

# built-in
import asyncio

# module under test
from vcorelib.task import Phony, Task


def test_task_basic():
    """Test basic task execution."""

    async def tasks(task: Task) -> None:
        """Add task dependencies and then dispatch the original task."""
        task.depend_on_all([Task("b"), Task("c")])
        await task.dispatch()
        await task.dispatch()

    task_a = Phony("a")
    asyncio.run(tasks(task_a))
    assert task_a.times_invoked == 2
