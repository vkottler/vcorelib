"""
Common path manipulation utilities.
"""

# built-in
from hashlib import md5 as _md5
from os import stat_result as _stat_result
from pathlib import Path as _Path
from typing import Iterable as _Iterable
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

# third-party
from pkg_resources import resource_filename as _resource_filename

# internal
from vcorelib import DEFAULT_ENCODING as _DEFAULT_ENCODING

Pathlike = _Union[_Path, str, None]


def normalize(path: Pathlike, *parts: _Union[str, _Path]) -> _Path:
    """Normalize an input that could be a path into a path."""
    path = (
        _Path("." if path is None else path)
        if not isinstance(path, _Path)
        else path
    )
    return path.joinpath(*parts)


def stats(path: Pathlike) -> _Optional[_stat_result]:
    """Get stats for a file on disk if it exists."""

    result = None
    path = normalize(path)
    if path.exists():
        result = path.stat()
    return result


def modified_ns(path: Pathlike) -> _Optional[int]:
    """Get the last-modified time from a path if the data can be obtained."""

    result = None
    stat = stats(path)
    if stat is not None:
        result = stat.st_mtime_ns
    return result


def modified_after(path: Pathlike, candidates: _Iterable[Pathlike]) -> bool:
    """
    Check if any candidate paths are more recently modified than the provided
    path. If the path doesn't exists but one or more of the candidates do, this
    method returns True.
    """

    mtime = modified_ns(path)

    # Use zero to compare so that even candidates that exist meet the criteria
    # for being updated after path.
    if mtime is None:
        mtime = 0

    for candidate in candidates:
        curr_mtime = modified_ns(candidate)
        if curr_mtime is not None and curr_mtime > mtime:
            return True

    return False


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


def str_md5_hex(data: str, encoding: str = _DEFAULT_ENCODING) -> str:
    """Get an md5 hex string from string data."""
    return _md5(bytes(data, encoding)).hexdigest()


def file_md5_hex(path: Pathlike) -> str:
    """Get an md5 hex string for a file by path."""
    with normalize(path).open("rb") as stream:
        return _md5(stream.read()).hexdigest()


def find_file(
    path: Pathlike,
    *parts: _Union[str, _Path],
    search_paths: _Iterable[Pathlike] = None,
    include_cwd: bool = False,
    relative_to: Pathlike = None,
    package: str = None,
    package_subdir: str = "data",
) -> _Optional[_Path]:
    """Combines a few simple strategies to locate a file on disk."""

    path = normalize(path, *parts)

    # If path is absolute we can't search for it.
    if path.is_absolute():
        if path.exists():
            return path
        return None

    to_check: _List[Pathlike] = []

    # Add a package resource to the search path if a package name was provided.
    if package is not None:
        to_check.append(_resource_filename(package, package_subdir))

    if search_paths:
        to_check += list(search_paths)

    # Check the working directory if it was specified.
    if include_cwd:
        to_check.append(_Path.cwd())

    # Check if the provided path exists relative to some other path.
    if relative_to is not None:
        relative_to = normalize(relative_to)
        to_check.append(
            relative_to if relative_to.is_dir() else relative_to.parent
        )

    # Return the first file we find on the search path, if we find one.
    for search in [normalize(x) for x in to_check]:
        if search.is_dir():
            candidate = search.joinpath(path)
            if candidate.exists():
                return candidate

    return None


# An alias for 'find_file' for convenience.
resource = find_file
