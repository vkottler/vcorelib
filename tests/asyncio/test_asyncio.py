"""
Test the 'asyncio' module.
"""

# built-in
import asyncio
from contextlib import suppress
from multiprocessing import Process
from os import kill
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Callable

# internal
from tests.asyncio.interrupt_tester import task_runner

# module under test
from vcorelib.asyncio import run_handle_stop

TestIteration = Callable[[int], bool]


def iterative_tester(test: TestIteration, iterations: int) -> bool:
    """Run a test until it passes."""

    success = False
    for i in range(iterations):
        success = test(i)
        if success:
            break

    return success


def handle_interrupt_process_test(idx: int) -> bool:
    """Attempt to trigger the interrupt handling logic."""

    proc = Process(target=task_runner, daemon=True)
    proc.start()

    # Wait some time to ensure that it has started sleeping.
    time.sleep(0.2 * idx)

    # Send SIGTERM.
    assert proc.pid is not None
    kill(proc.pid, getattr(signal, "CTRL_C_EVENT", signal.SIGINT))

    # Wait for it to clean up.
    proc.join()
    success = proc.exitcode == 0
    proc.close()

    return success


def test_run_handle_interrupt_process():
    """
    Test that we can gracefully shut down processes running in an event loop.
    """

    assert iterative_tester(
        handle_interrupt_process_test, 10
    ), "Never caught interrupt!"


def handle_interrupt_subprocess_test(idx: int) -> bool:
    """
    Test that we can gracefully shut down processes running in an event loop
    in a sub-process.
    """

    with subprocess.Popen(
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "-a",
            str(Path(__file__).with_name("interrupt_tester.py")),
        ],
    ) as proc:
        time.sleep(0.2 * idx)

        # Send a platform-specific signal.
        kill(proc.pid, getattr(signal, "CTRL_C_EVENT", signal.SIGINT))

        # This will raise an exception if reached.
        with suppress(subprocess.TimeoutExpired):
            proc.wait(timeout=1.0)

        result = proc.returncode == 0
    return result


def test_run_handle_interrupt_subprocess():
    """Test graceful shutdown behavior in a real sub-process."""

    assert iterative_tester(
        handle_interrupt_subprocess_test, 10
    ), "Never caught interrupt!"


def test_run_handle_stop_basic():
    """Test basic scenarios for the run_handle_stop method."""

    async def task() -> bool:
        """A sample task."""
        return True

    assert run_handle_stop(asyncio.Event(), task()) is True
