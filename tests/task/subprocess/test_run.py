"""
Test the 'task.subprocess.run' module.
"""

# third-party
import pytest

# module under test
from vcorelib.task.subprocess.run import (
    SubprocessExec,
    SubprocessExecStreamed,
    SubprocessShell,
    SubprocessShellStreamed,
)


@pytest.mark.asyncio
async def test_task_subprocess_run_exec_basic():
    """Test that we can run a basic subprocess."""

    # Test that the default task works.
    task = SubprocessExec("test")
    task.outbox["a"] = 1
    task.outbox["b"] = 2
    task.outbox["c"] = 3
    await task.dispatch()
    assert task.outbox["code"] == 0


@pytest.mark.asyncio
async def test_task_subprocess_run_shell_basic():
    """Test that we can run a basic shell command."""

    task = SubprocessShell("test")
    await task.dispatch()
    assert task.outbox["code"] == 0


@pytest.mark.asyncio
async def test_task_subprocess_run_streamed_basic():
    """Test streamed versions of subprocess and shell command tasks."""

    task = SubprocessExecStreamed("test")
    await task.dispatch()
    assert task.outbox["code"] == 0

    task = SubprocessShellStreamed("test")
    await task.dispatch()
    assert task.outbox["code"] == 0
