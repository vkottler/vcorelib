"""
A module implementing a file-info cache.
"""

# built-in
from contextlib import contextmanager as _contextmanager
from pathlib import Path as _Path
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import Iterator as _Iterator
from typing import NamedTuple as _NamedTuple
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import cast as _cast

# internal
from vcorelib.dict.cache import DirectoryCache, FileCache
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import file_md5_hex as _file_md5_hex
from vcorelib.paths import normalize as _normalize
from vcorelib.paths import stats as _stats


class FileInfo(_NamedTuple):
    """A collection of data to describe an identity of a file."""

    path: _Path
    size: int
    md5_hex: str

    def __eq__(self, other: object) -> bool:
        """Determine if two file info's are equivalent."""
        return self.path.samefile(_cast(FileInfo, other).path)

    def __hash__(self) -> int:
        """Get a hash for this file info based on the file name."""
        return hash(str(self.path.resolve()))

    def same(self, other: "FileInfo") -> bool:
        """Check if two file info contents match."""
        return other.size == self.size and other.md5_hex == self.md5_hex

    @staticmethod
    def from_file(path: _Pathlike) -> "FileInfo":
        """Create file info from a file."""

        path = _normalize(path).resolve()
        assert path.is_file()
        stats = _stats(path)
        assert stats is not None
        md5_hex = _file_md5_hex(path)
        return FileInfo(path, stats.st_size, md5_hex)

    def poll(self) -> _Tuple[bool, _Optional["FileInfo"]]:
        """Determine if this file is in a new state or not."""

        if not self.path.is_file():
            return True, None
        new_info = FileInfo.from_file(self.path)
        return self.same(new_info), new_info

    def to_json(self, data: _JsonObject = None) -> _JsonObject:
        """Get JSON data for this instance."""
        if data is None:
            data = {}

        path_str = str(self.path.resolve())
        if path_str not in data:
            data[path_str] = {}

        to_update = _cast(_JsonObject, data[path_str])
        to_update["size"] = self.size
        to_update["md5_hex"] = self.md5_hex

        return data

    @staticmethod
    def from_json(data: dict) -> _Dict[_Path, "FileInfo"]:
        """Create file info from JSON data."""

        result = {}
        for key, info in data.items():
            path = _Path(key)
            if path.is_file():
                result[path] = FileInfo(path, info["size"], info["md5_hex"])
        return result


#
# new file (if still present), old file (if it was previously present)
#
FileFreshCallback = _Callable[[_Optional[FileInfo], _Optional[FileInfo]], None]


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

        old_info = None
        norm = _normalize(path).resolve()
        to_del = []

        # Don't do anything if this isn't a file.
        if norm.is_file():
            info = FileInfo.from_file(norm)

            if norm in self.infos:
                old_info = self.infos[info.path]
                # If we know something about this file and it has changed,
                # invoke the callback.
                if not info.same(old_info):
                    self.poll(info, old_info)

            # If the file didn't exist when we last polled, invoke the
            # callback.
            else:
                self.poll(info, old_info)

            self.infos[info.path] = info

        # If we have previous info on the file but it's not present now, invoke
        # the callback.
        elif norm in self.infos:
            self.poll(None, self.infos[norm])
            to_del.append(norm)

        for old in to_del:
            del self.infos[old]


@_contextmanager
def file_info_cache(
    cache_path: _Pathlike, poll_cb: FileFreshCallback
) -> _Iterator[FileInfoManager]:
    """Obtain a file-info manager as a cached context."""

    path = _normalize(cache_path)
    cache = DirectoryCache if path.is_dir() else FileCache
    with cache(path).loaded() as data:
        manager = FileInfoManager(poll_cb, FileInfo.from_json(data))
        yield manager

        # Update dictionary data with the current cache contents.
        for info in manager.infos.values():
            info.to_json(data)
