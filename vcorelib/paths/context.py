"""
A module for context managers related to file-system paths.
"""

# built-in
from contextlib import contextmanager
from os import chdir as _chdir
from pathlib import Path as _Path
from typing import Iterator as _Iterator


@contextmanager
def in_dir(path: _Path) -> _Iterator[None]:
    """Change the current working directory as a context manager."""

    cwd = _Path.cwd()
    try:
        _chdir(path)
        yield
    finally:
        _chdir(cwd)
