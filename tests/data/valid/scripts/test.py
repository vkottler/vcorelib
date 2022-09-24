"""
A sample script.
"""

# third-party
from vcorelib.task import Task
from vcorelib.task.manager import TaskManager


def test(one: int, two: int, three: int, **kwargs: int) -> int:
    """Return the sum of the arguments."""

    return one + two + three + kwargs["four"] + kwargs["five"] + kwargs["six"]


def test_obj(manager: TaskManager, name: str, *args, **kwargs) -> int:
    """Test that we can register a task to a task manager."""

    manager.register(Task(name, *args, **kwargs))
    return 0
