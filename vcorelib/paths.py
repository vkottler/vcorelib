"""
Common path manipulation utilities.
"""

# built-in
from pathlib import Path
from typing import Union

Pathlike = Union[Path, str, None]


def normalize(path: Pathlike) -> Path:
    """Normalize an input that could be a path into a path."""
    return Path("." if path is None else path)


def get_file_name(path: Pathlike, maxsplit: int = -1) -> str:
    """
    From a path to a file, get the name of the file. Use 'maxsplit' to control
    how many suffixes are considered part of the name or the extension.
    """
    return ".".join(normalize(path).name.split(".", maxsplit=maxsplit)[:-1])


def get_file_ext(path: Pathlike, maxsplit: int = -1) -> str:
    """
    From a path to a file, get the file's extension. Use 'maxsplit' to control
    how many suffixes are considered part of the name or the extension.
    """
    return normalize(path).name.split(".", maxsplit=maxsplit)[-1]
