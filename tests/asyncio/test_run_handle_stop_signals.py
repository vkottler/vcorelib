"""
Test 'run_handle_stop' scenarios from the 'asyncio' module.
"""

# built-in
import asyncio
from multiprocessing import Process
import os
import signal
import sys
from time import sleep

# module under test
from vcorelib.asyncio import run_handle_stop


async def waiter(sig: asyncio.Event) -> None:
    """Sleep for some amount of time."""
    await asyncio.wait_for(sig.wait(), 10)


def sample_app() -> None:
    """An application that does nothing."""

    sig = asyncio.Event()
    run_handle_stop(sig, waiter(sig), signals=[signal.SIGTERM])

    # Return 0 if the signal is set, 1 if not.
    sys.exit(int(not sig.is_set()))


def sample_app_no_signals() -> None:
    """An application that does nothing."""

    sig = asyncio.Event()
    run_handle_stop(sig, waiter(sig))

    # Return 0 if the signal is set, 1 if not.
    sys.exit(int(not sig.is_set()))


def test_run_handle_stop_signals():
    """Test handling various stop signals."""

    proc = Process(target=sample_app)
    proc.start()
    sleep(0.1)

    proc.terminate()

    proc.join()
    assert proc.exitcode == 0

    proc = Process(target=sample_app_no_signals)
    proc.start()
    sleep(0.1)

    assert proc.pid is not None
    os.kill(proc.pid, signal.SIGINT)

    proc.join()
    assert proc.exitcode == 0
