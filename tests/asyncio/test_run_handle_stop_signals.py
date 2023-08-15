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


async def wait_n_events(sig: asyncio.Event, count: int = 1) -> None:
    """Wait on an event some n number of times."""

    while count > 0:
        await sig.wait()
        count -= 1

        if count > 0:
            sig.clear()


async def waiter(sig: asyncio.Event, count: int = 1) -> None:
    """Sleep for some amount of time."""
    await asyncio.wait_for(wait_n_events(sig, count=count), 10)


def sample_app() -> None:
    """An application that does nothing."""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    sig = asyncio.Event()
    run_handle_stop(
        sig,
        waiter(sig),
        signals=list(all_stop_signals()),
        eloop=loop,
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


def sample_app_wait_two() -> None:
    """An application that does nothing."""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    sig = asyncio.Event()
    run_handle_stop(
        sig,
        waiter(sig, count=2),
        signals=list(all_stop_signals()),
        eloop=loop,
    )

    # Return 0 if the signal is set, 1 if not.
    sys.exit(int(not sig.is_set()))


def sample_app_wait_two_no_signals() -> None:
    """An application that does nothing."""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    sig = asyncio.Event()
    run_handle_stop(sig, waiter(sig, count=2), eloop=loop)

    # Return 0 if the signal is set, 1 if not.
    sys.exit(int(not sig.is_set()))


def test_run_handle_stop_multiple_signals():
    """Test run_handle_stop multiple interrupt signal behavior."""

    for target in [sample_app_wait_two, sample_app_wait_two_no_signals]:
        proc = Process(target=target)
        proc.start()

        assert proc.pid is not None

        sleep(0.25)
        os.kill(proc.pid, signal.SIGINT)
        sleep(0.25)
        os.kill(proc.pid, signal.SIGINT)

        # Sometimes the process doesn't get far enough after the sleep.
        proc.join()
        assert proc.exitcode is not None

        # The program exits because of the uncaught keyboard interrupt.
        if target is sample_app_wait_two_no_signals:
            assert abs(proc.exitcode) != 0
        else:
            assert abs(proc.exitcode) in (0, signal.SIGINT)


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
