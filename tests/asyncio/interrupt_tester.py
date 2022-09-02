"""
A module for testing the interrupt-handling behavior of 'run_handle_interrupt'
and async sub-process management.
"""

# built-in
import asyncio
from contextlib import suppress
from os import remove
import signal
import sys
import tempfile
from textwrap import dedent

# module under test
from vcorelib.asyncio import run_handle_interrupt
from vcorelib.task import TaskFailed
from vcorelib.task.subprocess.run import SubprocessExecStreamed


def interrupt_raiser(*_) -> None:
    """Un-conditionally raise a keyboard interrupt."""
    print("Got interrupt signal!")
    raise KeyboardInterrupt()


def task_runner() -> None:
    """Run an event-loop task that will spawn a process that sleeps."""

    for sig in list(
        {
            signal.SIGINT,
            signal.SIGBREAK,
            getattr(signal, "CTRL_C_EVENT", signal.SIGINT),
            getattr(signal, "CTRL_BREAK_EVENT", signal.SIGINT),
            signal.SIGTERM,
        }
    ):
        # Install signal handlers to translate terminations to
        # KeyboardInterrupt.
        with suppress(ValueError):
            signal.signal(sig, interrupt_raiser)

    program = """
    sleep_time = 2
    print(f"Starting {sleep_time} second sleep.")

    import time
    try:
        time.sleep(sleep_time)
        print(f"Finished {sleep_time} second sleep.")
    except KeyboardInterrupt:
        print("Inline script got interrupted!")
    """

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as temp:
        temp.write(dedent(program).strip())
        temp.flush()
        name = temp.name

    try:
        task = SubprocessExecStreamed("sleeper", name, args="")

        # Create an event-loop and ensure it's associated with the
        # main thread.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        with suppress(TaskFailed):
            run_handle_interrupt(task.dispatch(), loop)

    finally:
        remove(name)

    sys.exit(1)


if __name__ == "__main__":
    task_runner()
