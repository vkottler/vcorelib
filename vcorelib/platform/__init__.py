"""
A module implementing utilities for performing tasks on differing platforms.
"""

# built-in
from platform import system as _system
from typing import Iterable as _Iterable
from typing import List as _List
from typing import Tuple as _Tuple


def is_windows() -> bool:
    """Determine if the current platform is Windows or not."""
    return _system() == "Windows"


def reconcile_platform(
    program: str, args: _Iterable[str]
) -> _Tuple[str, _List[str]]:
    """
    Handle arguments for Windows. You cannot run a program directly on Windows
    under any circumstance, so pass arguments through to the shell.
    """

    list_args = list(args)
    list_args = ["/c", program] + list_args if is_windows() else list_args
    program = "cmd.exe" if is_windows() else program
    return program, list_args
