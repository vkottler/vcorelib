"""
A module for working with asyncio.
"""

from __future__ import annotations

# built-in
from asyncio import AbstractEventLoop as _AbstractEventLoop
from asyncio import CancelledError as _CancelledError
from asyncio import Event as _Event
from asyncio import Task as _Task
from asyncio import all_tasks as _all_tasks
from asyncio import get_event_loop as _get_event_loop
from contextlib import ExitStack, contextmanager
from contextlib import suppress as _suppress
from logging import getLogger as _getLogger
import signal as _signal
from types import FrameType as _FrameType
from typing import Any as _Any
from typing import Awaitable as _Awaitable
from typing import Callable as _Callable
from typing import Coroutine as _Coroutine
from typing import Iterable as _Iterable
from typing import Iterator
from typing import List as _List
from typing import Optional as _Optional
from typing import Set as _Set
from typing import TypeVar as _TypeVar

# internal
from vcorelib.logging import LoggerType as _LoggerType

T = _TypeVar("T")
LOG = _getLogger(__name__)


def log_task_exception(task: _Task[_Any], logger: _LoggerType = None) -> None:
    """If a task is done and raised an exception, log it."""

    if logger is None:
        logger = LOG

    if task.done():
        with _suppress(_CancelledError):
            exc = task.exception()
            if (
                exc is not None
                and not isinstance(exc, _CancelledError)
                and not isinstance(exc, KeyboardInterrupt)
            ):
                logger.exception("Task raised exception:", exc_info=exc)


def log_exceptions(
    tasks: _Iterable[_Task[T]], logger: _LoggerType = None
) -> _List[_Task[T]]:
    """Log task exception and return the list of tasks that aren't complete."""

    for task in tasks:
        log_task_exception(task, logger=logger)
    return [x for x in tasks if not x.done()]


def normalize_eloop(eloop: _AbstractEventLoop = None) -> _AbstractEventLoop:
    """Get the active event loop if one isn't provided explicitly."""

    if eloop is None:
        eloop = _get_event_loop()
    return eloop


def shutdown_loop(
    eloop: _AbstractEventLoop = None, logger: _LoggerType = None
) -> None:
    """Attempt to shut down an event loop."""

    eloop = normalize_eloop(eloop)
    eloop.run_until_complete(eloop.shutdown_asyncgens())

    tasks = log_exceptions(_all_tasks(loop=eloop), logger=logger)
    if tasks:
        # Cancel all tasks running in the event loop.
        for task in tasks:
            task.cancel()

            # Give all tasks a chance to complete.
            with _suppress(KeyboardInterrupt, _CancelledError):
                eloop.run_until_complete(task)
                log_task_exception(task, logger=logger)


def run_handle_interrupt(
    to_run: _Awaitable[_Any],
    eloop: _AbstractEventLoop = None,
    enable_uvloop: bool = True,
) -> _Optional[_Any]:
    """
    Run a task in an event loop and gracefully handle keyboard interrupts.

    Return the result of the awaitable or None if execution was interrupted.
    """

    with try_uvloop_runner(eloop=eloop, enable=enable_uvloop) as loop:
        result = None
        try:
            result = loop.run_until_complete(to_run)
        except KeyboardInterrupt:
            shutdown_loop(loop)

    return result


SignalHandler = _Callable[[int, _Optional[_FrameType]], None]


def event_setter(
    stop_sig: _Event,
    eloop: _AbstractEventLoop = None,
    logger: _LoggerType = None,
) -> SignalHandler:
    """Create a function that sets an event."""

    if logger is None:
        logger = LOG

    def setter(sig: int, _: _Optional[_FrameType]) -> None:
        """Set the signal."""

        rep = f"{sig} ({_signal.Signals(sig).name})"
        LOG.info("Received signal %s.", rep)

        # Ensure scheduling 'stop_sig.set' is a nominal reaction to this
        # signal. If not, raise an exception.
        assert (
            not stop_sig.is_set()
        ), "Stop signal is set but received signal {rep}!"

        normalize_eloop(eloop).call_soon_threadsafe(stop_sig.set)

    return setter


def all_stop_signals() -> _Set[int]:
    """Get a set of all stop signals on this platform."""

    return {
        _signal.SIGINT,
        getattr(_signal, "SIGBREAK", _signal.SIGINT),
        getattr(_signal, "CTRL_C_EVENT", _signal.SIGINT),
        getattr(_signal, "CTRL_BREAK_EVENT", _signal.SIGINT),
        _signal.SIGTERM,
    }


@contextmanager
def try_uvloop_runner(
    debug: bool = None, eloop: _AbstractEventLoop = None, enable: bool = True
) -> Iterator[_AbstractEventLoop]:
    """Try to set up an asyncio runner using uvloop."""

    # pylint: disable=import-outside-toplevel

    with ExitStack() as stack:
        if enable and eloop is None:
            with _suppress(ImportError):
                import uvloop

                try:
                    from asyncio import Runner

                    eloop = stack.enter_context(
                        Runner(debug=debug, loop_factory=uvloop.new_event_loop)
                    ).get_loop()
                except ImportError:  # pragma: nocover
                    uvloop.install()

        yield normalize_eloop(eloop)

    # pylint: enable=import-outside-toplevel


def run_handle_stop(
    stop_sig: _Event,
    task: _Coroutine[None, None, T],
    eloop: _AbstractEventLoop = None,
    signals: _Iterable[int] = None,
    enable_uvloop: bool = True,
) -> T:
    """
    Publish the stop signal on keyboard interrupt and wait for the task to
    complete.
    """

    with try_uvloop_runner(eloop=eloop, enable=enable_uvloop) as loop:
        to_run = loop.create_task(task)

        # Register signal handlers if signals were provided.
        if signals is not None:
            setter = event_setter(stop_sig, eloop=loop)
            for signal in signals:
                _signal.signal(signal, setter)

        while True:
            try:
                return loop.run_until_complete(to_run)
            except KeyboardInterrupt:
                print("Keyboard interrupt.")
                assert not stop_sig.is_set(), "Stop signal already set!"
                loop.call_soon_threadsafe(stop_sig.set)
