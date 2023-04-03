"""
A module implementing a file-info cache.
"""

# built-in
from contextlib import contextmanager as _contextmanager
from pathlib import Path as _Path
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import Iterator as _Iterator
from typing import Optional as _Optional

# internal
from vcorelib.dict.cache import FileCache
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize as _normalize
from vcorelib.paths.info import FileInfo

#
# new file (if still present), old file (if it was previously present)
#
# return True if the callback succeeded, in this case an implementation using
# this callback should consider the new file info valid
#
# if False was returned, do not promote the new file info into any cache or
# runtime state
#
# this return-value signal is useful because software that acts on file changes
# can fail, and eventually retry later (such as in a completely new invocation
# of the program), without the file-change event being lost
#
FileFreshCallback = _Callable[[_Optional[FileInfo], _Optional[FileInfo]], bool]

# Adds 'FileInfo' from the .info module.
__all__ = [
    "FileFreshCallback",
    "FileInfoManager",
    "file_info_cache",
    "FileInfo",
]


class FileInfoManager:
    """A class simplifying evaluation of changes to files on disk."""

    def __init__(
        self,
        poll_cb: FileFreshCallback,
        initial: _Dict[_Path, FileInfo] = None,
    ) -> None:
        """Initialize this file-info manager."""

        self.poll = poll_cb

        if initial is None:
            initial = {}
        self.infos = initial

        # If we have initial files, poll them all.
        for path in list(self.infos.keys()):
            self.poll_file(path)

    def poll_directory(self, path: _Pathlike, recurse: bool = True) -> None:
        """Poll an entire directory for changes."""

        norm = _normalize(path).resolve()

        # Don't do anything if this isn't a directory.
        if norm.is_dir():
            for item in norm.iterdir():
                if item.is_file():
                    self.poll_file(item)
                    continue

                if recurse:
                    self.poll_directory(item)

    def poll_file(self, path: _Pathlike) -> None:
        """Check if a file has changed and invoke the callback if so."""

        norm = _normalize(path).resolve()
        old_info = self.infos.get(norm)

        info = None
        if norm not in self.infos:
            info = FileInfo.from_file(norm)
            new = True
        else:
            new, info = self.infos[norm].poll()

        if new:
            # Don't update internal state if the callback signals us not to.
            if not self.poll(info, old_info):
                return

        if info is not None:
            self.infos[info.path] = info
        else:
            del self.infos[norm]


@_contextmanager
def file_info_cache(
    cache_path: _Pathlike, poll_cb: FileFreshCallback
) -> _Iterator[FileInfoManager]:
    """Obtain a file-info manager as a cached context."""

    path = _normalize(cache_path)
    assert not path.is_dir(), f"'{path}' is a directory!"
    with FileCache(path).loaded() as data:
        manager = FileInfoManager(poll_cb, FileInfo.from_json(data))
        yield manager

        # Update dictionary data with the current cache contents.
        for info in manager.infos.values():
            info.to_json(data)
