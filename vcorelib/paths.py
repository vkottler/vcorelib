"""
Common path manipulation utilities.
"""

# built-in
from pathlib import Path as _Path
from typing import Union as _Union

Pathlike = _Union[_Path, str, None]


def normalize(path: Pathlike) -> _Path:
    """Normalize an input that could be a path into a path."""
    return (
        _Path("." if path is None else path)
        if not isinstance(path, _Path)
        else path
    )


def get_file_name(path: Pathlike, maxsplit: int = -1) -> str:
    """
    From a path to a file, get the name of the file. Use 'maxsplit' to control
    how many suffixes are considered part of the name or the extension.
    """
    split = normalize(path).name.split(".", maxsplit=maxsplit)
    if len(split) > 1:
        pieces = split[:-1]
    else:
        pieces = [split[0]]
    return ".".join(pieces)


def get_file_ext(path: Pathlike, maxsplit: int = -1) -> str:
    """
    From a path to a file, get the file's extension. Use 'maxsplit' to control
    how many suffixes are considered part of the name or the extension.
    """
    return normalize(path).name.split(".", maxsplit=maxsplit)[-1]
