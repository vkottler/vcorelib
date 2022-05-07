"""
Test the 'task.dict.merger' module.
"""

# built-in
import asyncio

# module under test
from vcorelib.task import Task
from vcorelib.task.dict.melder import DictMerger


def test_dict_merger_basic():
    """Verify that dict-merger tasks work correctly."""

    async def tasks(task: Task) -> None:
        """Add task dependencies and then dispatch the original task."""
        task.depend_on_all(
            [
                DictMerger("a", {"a": 1}),
                DictMerger("b", {"b": 2}),
                DictMerger("c", {"c": 3}),
            ]
        )
        await task.dispatch()

    task = Task("test")
    asyncio.run(tasks(task))

    # Verify that data was merged.
    assert task.inbox == {"a": {"a": 1}, "b": {"b": 2}, "c": {"c": 3}}
