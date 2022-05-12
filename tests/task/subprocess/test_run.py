"""
Test the 'task.subprocess.run' module.
"""

# built-in
import asyncio

# module under test
from vcorelib.task.subprocess.run import SubprocessExec, SubprocessShell


def test_task_subprocess_run_exec_basic():
    """Test that we can run a basic subprocess."""

    # Test that the default task works.
    task = SubprocessExec("test")
    task.outbox["a"] = 1
    task.outbox["b"] = 2
    task.outbox["c"] = 3
    asyncio.run(task.dispatch())
    assert task.outbox["code"] == 0


def test_task_subprocess_run_shell_basic():
    """Test that we can run a basic shell command."""

    task = SubprocessShell("test")
    asyncio.run(task.dispatch())
    assert task.outbox["code"] == 0
