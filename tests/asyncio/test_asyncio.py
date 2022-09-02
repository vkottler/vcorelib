"""
Test the 'asyncio' module.
"""

# built-in
from multiprocessing import Process
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Callable

# internal
from tests.asyncio.interrupt_tester import task_runner

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

    proc = Process(target=task_runner)
    proc.start()

    # Wait some time to ensure that it has started sleeping.
    time.sleep(0.1 * idx)

    # Send SIGTERM.
    proc.terminate()

    # Wait for it to clean up.
    proc.join()
    success = proc.exitcode == 1
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
            "-a",
            str(Path(__name__).with_name("interrupt_tester.py")),
        ],
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    ) as proc:
        time.sleep(0.1 * idx)

        # Send a platform-specific signal.
        proc.send_signal(getattr(signal, "CTRL_C_EVENT", signal.SIGINT))

        # This will raise an exception if reached.
        proc.wait(timeout=6.0)

        result = proc.returncode == 1
    return result


def test_run_handle_interrupt_subprocess():
    """Test graceful shutdown behavior in a real sub-process."""

    assert iterative_tester(
        handle_interrupt_subprocess_test, 10
    ), "Never caught interrupt!"
