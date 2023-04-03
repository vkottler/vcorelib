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
from typing import Union as _Union

# internal
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize as _normalize


@contextmanager
def in_dir(
    path: _Pathlike, *parts: _Union[str, _Path], makedirs: bool = False
) -> _Iterator[_Path]:
    """Change the current working directory as a context manager."""

    cwd = _Path.cwd()
    try:
        path = _normalize(path, *parts)
        if makedirs:
            _makedirs(path, exist_ok=True)
        _chdir(path)
        yield path
    finally:
        _chdir(cwd)


@contextmanager
def linked_to(
    link: _Pathlike,
    target: _Pathlike,
    *parts: _Union[str, _Path],
    target_is_directory: bool = False,
) -> _Iterator[_Path]:
    """Provide a symbolic link as a managed context."""

    link = _normalize(link)
    link.symlink_to(
        _normalize(target, *parts), target_is_directory=target_is_directory
    )

    try:
        yield link
    finally:
        link.unlink()


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
