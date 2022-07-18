"""
A module for context managers related to file-system paths.
"""

# built-in
from contextlib import contextmanager, suppress
from os import chdir as _chdir
from os import makedirs as _makedirs
from pathlib import Path as _Path
from tempfile import NamedTemporaryFile as _NamedTemporaryFile
from typing import Iterator as _Iterator

# internal
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize as _normalize


@contextmanager
def in_dir(path: _Pathlike, makedirs: bool = False) -> _Iterator[None]:
    """Change the current working directory as a context manager."""

    cwd = _Path.cwd()
    try:
        path = _normalize(path)
        if makedirs:
            _makedirs(path, exist_ok=True)
        _chdir(path)
        yield
    finally:
        _chdir(cwd)


@contextmanager
def tempfile(*args, **kwargs) -> _Iterator[_Path]:
    """
    Get a valid path to a temporary file and guarantee that its cleaned up
    afterwards.
    """

    with _NamedTemporaryFile(*args, **kwargs) as temp:
        path = _Path(temp.name)
    try:
        yield path
    finally:
        with suppress(FileNotFoundError):
            # Respect the 'delete' argument.
            if kwargs.get("delete", True):
                path.unlink()
