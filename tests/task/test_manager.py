"""
Test the 'task.manager' module.
"""

# module under test
from vcorelib.task import Task
from vcorelib.task.manager import TaskManager


def test_task_manager_basic():
    """Test basic interactions with a task manager."""

    manager = TaskManager()
    manager.register(Task("a"))
    manager.register(Task("b"))
    manager.register(Task("c"))
    manager.register(Task("test"), ["a", "b", "c"])
    manager.execute(["test"])
    manager.execute(["test"])
