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
from vcorelib.asyncio import all_stop_signals, run_handle_stop


async def waiter(sig: asyncio.Event) -> None:
    """Sleep for some amount of time."""
    await asyncio.wait_for(sig.wait(), 10)


def sample_app() -> None:
    """An application that does nothing."""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    sig = asyncio.Event()
    run_handle_stop(
        sig, waiter(sig), signals=list(all_stop_signals()), eloop=loop
    )

    # Return 0 if the signal is set, 1 if not.
    sys.exit(int(not sig.is_set()))


def sample_app_no_signals() -> None:
    """An application that does nothing."""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    sig = asyncio.Event()
    run_handle_stop(sig, waiter(sig), eloop=loop)

    # Return 0 if the signal is set, 1 if not.
    sys.exit(int(not sig.is_set()))


def test_run_handle_stop_signals():
    """Test handling various stop signals."""

    proc = Process(target=sample_app)
    proc.start()
    sleep(0.25)

    proc.terminate()

    # Sometimes the process doesn't get far enough after the sleep.
    proc.join()
    assert proc.exitcode is not None
    assert abs(proc.exitcode) in (0, signal.SIGTERM)

    proc = Process(target=sample_app_no_signals)
    proc.start()
    sleep(0.25)

    assert proc.pid is not None
    os.kill(proc.pid, signal.SIGINT)

    # Sometimes the process doesn't get far enough after the sleep.
    proc.join()
    assert proc.exitcode is not None
    assert abs(proc.exitcode) in (0, signal.SIGINT)
