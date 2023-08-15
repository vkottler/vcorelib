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
from typing import Callable

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


def get_sample_app(count: int = 1, signals: bool = True) -> Callable[[], None]:
    """Get a sample app and provide the number of signals to wait on."""

    def sample_app() -> None:
        """An application that does nothing."""

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        sig = asyncio.Event()
        run_handle_stop(
            sig,
            waiter(sig, count=count),
            signals=list(all_stop_signals()) if signals else None,
            eloop=loop,
        )

        # Return 0 if the signal is set, 1 if not.
        sys.exit(int(not sig.is_set()))

    return sample_app


def sample_app_no_signals() -> None:
    """An application that does nothing."""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    sig = asyncio.Event()
    run_handle_stop(sig, waiter(sig), eloop=loop)

    # Return 0 if the signal is set, 1 if not.
    sys.exit(int(not sig.is_set()))


def test_run_handle_stop_multiple_signals():
    """TODO."""

    for signals in [False, True]:
        proc = Process(target=get_sample_app(2, signals=signals))
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
        if not signals:
            assert abs(proc.exitcode) != 0
        else:
            assert abs(proc.exitcode) in (0, signal.SIGTERM)


def test_run_handle_stop_signals():
    """Test handling various stop signals."""

    proc = Process(target=get_sample_app())
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
