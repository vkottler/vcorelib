"""
Common path manipulation utilities.
"""

# built-in
from typing import Iterable as _Iterable
from typing import Optional as _Optional

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
from vcorelib.paths.find import find_file
from vcorelib.paths.hashing import (
    DEFAULT_HASH,
    bytes_hash_hex,
    bytes_md5_hex,
    create_hex_digest,
    file_hash_hex,
    file_md5_hex,
    str_hash_hex,
    str_md5_hex,
    validate_hex_digest,
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
    "validate_hex_digest",
    "prune_empty_directories",
]


def modified_ns(path: Pathlike) -> _Optional[int]:
    """Get the last-modified time from a path if the data can be obtained."""

    result = None
    stat = stats(path)
    if stat is not None:
        result = stat.st_mtime_ns
    return result


def prune_empty_directories(path: Pathlike) -> None:
    """Attempt to prune empty directories from some path."""

    path = normalize(path)

    if path.is_dir():
        # Remove sub-directories.
        for subdir in path.iterdir():
            if subdir.is_dir():
                prune_empty_directories(subdir)

        # Remove this directory.
        if len(list(path.iterdir())) == 0:
            path.rmdir()


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


# An alias for 'find_file' for convenience.
resource = find_file
