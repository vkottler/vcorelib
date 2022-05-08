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

    manager.register_to("a", ["b", "c"])
    manager.register_to("b", ["c"])
    manager.execute(["test"])

    manager.finalized = False
    manager.execute(["test"], init_only=True)


def test_task_manager_dry_run():
    """Test that tasks behave correctly during 'init_only'."""

    manager = TaskManager()
    manager.register(Task("a"))
    manager.register(Task("b"))
    manager.register(Task("c"))
    manager.register(Task("test"), ["a", "b", "c"])
    manager.execute(["test"], init_only=True)
    assert manager.tasks["test"].resolved is False
