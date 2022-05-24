"""
Test the 'task' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark, raises

# module under test
from vcorelib.task import Inbox, Outbox, Phony, Task, TaskFailed


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


@mark.asyncio
async def test_task_fail():
    """Test that we can handle task failure."""

    class FailTask(Task):
        """A task that always fails."""

        async def run(
            self, inbox: Inbox, outbox: Outbox, *args, **kwargs
        ) -> bool:
            """Task fails by default."""
            return False

    # Ensure that the task fails.
    with raises(TaskFailed):
        await FailTask("test").dispatch(caller=Task("a"))
