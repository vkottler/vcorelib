"""
A module for testing the interrupt-handling behavior of 'run_handle_interrupt'
and async sub-process management.
"""

# built-in
import asyncio
import signal
import tempfile
from textwrap import dedent

# module under test
from vcorelib.asyncio import run_handle_interrupt
from vcorelib.task.subprocess.run import SubprocessExecStreamed


def interrupt_raiser(*_) -> None:
    """Un-conditionally raise a keyboard interrupt."""
    raise KeyboardInterrupt()


def task_runner() -> None:
    """Run an event-loop task that will spawn a process that sleeps."""

    # Install signal handlers to translate terminations to
    # KeyboardInterrupt.
    signal.signal(signal.SIGTERM, interrupt_raiser)

    program = """
    sleep_time = 5
    print(f"Starting {sleep_time} second sleep.")

    import time
    time.sleep(sleep_time)

    print(f"Finished {sleep_time} second sleep.")
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py") as temp:
        temp.write(dedent(program).strip())
        temp.flush()

        task = SubprocessExecStreamed(
            "sleeper",
            "-m",
            "coverage",
            "run",
            "-a",
            temp.name,
            args="",
        )

        # Create an event-loop and ensure it's associated with the
        # main thread.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        run_handle_interrupt(task.dispatch(), loop)


if __name__ == "__main__":
    task_runner()
