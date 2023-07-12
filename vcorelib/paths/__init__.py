"""
Common path manipulation utilities.
"""

# built-in
from logging import Logger as _Logger
from pathlib import Path as _Path
from typing import Iterable as _Iterable
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

# third-party
import importlib_resources as _importlib_resources

# internal
from vcorelib.paths.base import (
    Pathlike,
    get_file_ext,
    get_file_name,
    normalize,
    rel,
    set_exec_flags,
    stats,
)
from vcorelib.paths.hashing import (
    DEFAULT_HASH,
    bytes_hash_hex,
    bytes_md5_hex,
    create_hex_digest,
    file_hash_hex,
    file_md5_hex,
    str_hash_hex,
    str_md5_hex,
)

__all__ = [
    "Pathlike",
    "normalize",
    "stats",
    "modified_ns",
    "modified_after",
    "get_file_name",
    "get_file_ext",
    "DEFAULT_HASH",
    "bytes_hash_hex",
    "str_hash_hex",
    "file_hash_hex",
    "bytes_md5_hex",
    "str_md5_hex",
    "file_md5_hex",
    "set_exec_flags",
    "rel",
    "find_file",
    "resource",
    "create_hex_digest",
]


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


def _construct_search_path(
    search_paths: _Iterable[Pathlike] = None,
    include_cwd: bool = False,
    relative_to: Pathlike = None,
    package: str = None,
    package_subdir: str = "data",
    logger: _Logger = None,
) -> _List[Pathlike]:
    """Construct a list of paths to search for a resource."""

    to_check: _List[Pathlike] = []

    # Add a package resource to the search path if a package name was provided.
    if package is not None:
        try:
            to_check.append(
                _importlib_resources.files(package).joinpath(package_subdir)
            )
        except ModuleNotFoundError:
            if logger is not None:
                logger.warning(
                    "Can't search package '%s', not found.", package
                )

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

    return to_check


def find_file(
    path: Pathlike,
    *parts: _Union[str, _Path],
    search_paths: _Iterable[Pathlike] = None,
    include_cwd: bool = False,
    relative_to: Pathlike = None,
    package: str = None,
    package_subdir: str = "data",
    logger: _Logger = None,
) -> _Optional[_Path]:
    """Combines a few simple strategies to locate a file on disk."""

    path = normalize(path, *parts)

    # If path is absolute we can't search for it.
    if path.is_absolute():
        if path.exists():
            return path
        return None

    # Return the first file we find on the search path, if we find one.
    for search in [
        normalize(x)
        for x in _construct_search_path(
            search_paths=search_paths,
            include_cwd=include_cwd,
            relative_to=relative_to,
            package=package,
            package_subdir=package_subdir,
            logger=logger,
        )
    ]:
        if search.is_dir():
            candidate = search.joinpath(path)
            if candidate.exists():
                if logger is not None:
                    logger.debug("Found '%s' at '%s'.", path, search)
                return candidate

            if logger is not None:
                logger.debug("Didn't find '%s' at '%s'.", path, search)

    return None


# An alias for 'find_file' for convenience.
resource = find_file
