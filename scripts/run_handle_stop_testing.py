"""
A simple script for testing the behavior of run_handle_stop.
"""

# built-in
import asyncio
import logging
import sys
from typing import List

# internal
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


def app(
    sig: asyncio.Event,
    loop: asyncio.AbstractEventLoop,
    count: int,
    signals: bool,
) -> None:
    """Test some configuration of the application."""

    run_handle_stop(
        sig,
        waiter(sig, count=count),
        signals=list(all_stop_signals()) if signals else None,
        eloop=loop,
    )


def main(argv: List[str]) -> int:
    """Script entry."""

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(name)-36s - %(levelname)-6s - %(message)s",
    )

    del argv

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    sig = asyncio.Event()

    # app(sig, loop, 2, True)
    app(sig, loop, 2, False)

    # Return 0 if the signal is set, 1 if not.
    return int(not sig.is_set())


if __name__ == "__main__":
    sys.exit(main(sys.argv))
