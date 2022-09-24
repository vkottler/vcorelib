"""
A module for cache implementations - conforming to package-wide, data-structure
constraints and assumptions.
"""

# built-in
from collections import UserDict
from logging import DEBUG as _DEBUG
from logging import Logger
from pathlib import Path
from shutil import rmtree
from typing import MutableMapping as _MutableMapping

# third-party
from vcorelib.dict import merge
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io import DataArbiter

# internal
from vcorelib.io.archive import extractall, make_archive
from vcorelib.io.types import DEFAULT_ARCHIVE_EXT as _DEFAULT_ARCHIVE_EXT
from vcorelib.io.types import DEFAULT_DATA_EXT as _DEFAULT_DATA_EXT
from vcorelib.io.types import FileExtension
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue
from vcorelib.math.time import TIMER as _TIMER
from vcorelib.math.time import byte_count_str, nano_str
from vcorelib.paths import Pathlike as _Pathlike


class FlatDirectoryCache(
    UserDict,  # type: ignore
    _MutableMapping[str, _JsonValue],
):
    """
    A class implementing a dictionary that can be saved and loaded from disk,
    with a specified encoding scheme.
    """

    def __init__(
        self,
        root: Path,
        initialdata: _JsonObject = None,
        archive_encoding: str = _DEFAULT_ARCHIVE_EXT,
        data_encoding: str = _DEFAULT_DATA_EXT,
        arbiter: DataArbiter = _ARBITER,
        **load_kwargs,
    ) -> None:
        """Initialize this data cache."""

        super().__init__(initialdata)
        self.root = root
        self.archive_encoding = archive_encoding
        self.data_encoding = data_encoding
        self.arbiter = arbiter
        self.load_time_ns: int = -1
        self.save_time_ns: int = -1

        # A derived class must add logic to set this.
        self.changed: bool = False

        merge(self.data, self.load(self.root, **load_kwargs))

    def load_directory(
        self,
        path: _Pathlike,
        data: _JsonObject,
        **kwargs,
    ) -> int:
        """Load a directory and update data, return time taken to load."""

        load = self.arbiter.decode_directory(
            path, require_success=True, **kwargs
        )
        data.update(load.data)
        return load.time_ns

    def load(
        self,
        path: Path = None,
        logger: Logger = None,
        level: int = _DEBUG,
        **kwargs,
    ) -> _JsonObject:
        """Load data from disk."""

        if path is None:
            path = self.root

        loaded = False
        result: _JsonObject = {}
        if path.is_dir():
            self.load_time_ns = self.load_directory(path, result, **kwargs)
            loaded = True

        # See if we can locate an archive for this path, that we can extract
        # and then load.
        else:
            archive = FileExtension.has_archive(path)
            if archive is not None:
                success, time_ns = extractall(archive, path.parent)
                if success:
                    if logger is not None:
                        logger.log(
                            level,
                            "Extracted archive '%s' in %ss.",
                            archive,
                            nano_str(time_ns, True),
                        )
                    return self.load(path, logger, level, **kwargs)

        if loaded and logger is not None:
            logger.log(
                level,
                "Cache loaded in %ss.",
                nano_str(self.load_time_ns, True),
            )
        return result

    def save_directory(self, path: Path, **kwargs) -> int:
        """Write data in this cache to a directory."""

        path.mkdir(parents=True, exist_ok=True)
        return self.arbiter.encode_directory(
            path, self.data, self.data_encoding, **kwargs
        )[1]

    def save(
        self,
        path: Path = None,
        logger: Logger = None,
        level: int = _DEBUG,
        archive: bool = False,
        **kwargs,
    ) -> None:
        """Save data to disk."""

        if path is None:
            path = self.root

        if self.changed:
            self.save_time_ns = self.save_directory(path, **kwargs)

        # Create an archive for this cache if requested.
        if archive:
            result = make_archive(path, self.archive_encoding)
            assert result[0] is not None, "Tried to make archive but couldn't!"
            if logger is not None:
                logger.log(
                    level,
                    "Cache archived to '%s' (%s) in %ss.",
                    result[0],
                    byte_count_str(result[0].stat().st_size),
                    nano_str(result[1], True),
                )

        if self.changed and logger is not None:
            logger.log(
                level,
                "Cache written in %ss.",
                nano_str(self.save_time_ns, True),
            )
        self.changed = False

    def clean(
        self,
        path: Path = None,
        logger: Logger = None,
        level: int = _DEBUG,
    ) -> None:
        """Remove cached data from disk."""

        if path is None:
            path = self.root

        with _TIMER.measure_ns() as token:
            # Remove any archives.
            for candidate in FileExtension.archive_candidates(path, True):
                candidate.unlink()

            # Remove the data directory.
            rmtree(path, ignore_errors=True)

        time_ns = _TIMER.result(token)
        if logger is not None:
            logger.log(level, "Cache cleaned in %ss.", nano_str(time_ns, True))
