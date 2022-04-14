"""
Common type definitions for data encoding and decoding interfaces.
"""

# built-in
from enum import Enum
from io import StringIO
from logging import Logger
from pathlib import Path
from typing import Callable as _Callable
from typing import Iterator as _Iterator
from typing import List as _List
from typing import NamedTuple
from typing import Optional as _Optional
from typing import TextIO
from typing import Tuple as _Tuple
from typing import Union as _Union

# third-party
from ruamel.yaml import YAML

# internal
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import get_file_ext

DEFAULT_ARCHIVE_EXT = "tar.gz"
DEFAULT_DATA_EXT = "json"


class FileExtension(Enum):
    """A mapping of expected encoding type to file extensions."""

    UNKNOWN: _List[str] = ["unknown"]
    JSON: _List[str] = [DEFAULT_DATA_EXT]
    YAML: _List[str] = ["yaml", "yml", "eyaml"]
    INI: _List[str] = ["ini", "cfg"]
    ZIP: _List[str] = ["zip"]
    TAR: _List[str] = [
        DEFAULT_ARCHIVE_EXT,
        "tar",
        "tar.bz2",
        "tar.lzma",
        "tar.xz",
    ]
    TOML: _List[str] = ["toml"]

    def __str__(self) -> str:
        """Get this extension as a string."""
        return self.value[0]

    def is_archive(self) -> bool:
        """Determine if this extension is a kind of archive file."""
        return self in {FileExtension.ZIP, FileExtension.TAR}

    @staticmethod
    def has_archive(path: Path) -> _Optional[Path]:
        """Determine if a path has an associated archive file."""

        for ext in [FileExtension.ZIP, FileExtension.TAR]:
            for ext_str in ext.value:  # pylint: disable=not-an-iterable
                check_path = Path(f"{path}.{ext_str}")
                if check_path.is_file():
                    return check_path

        return None

    def is_data(self) -> bool:
        """Determine if this etension is a kind of data file."""
        return self in {
            FileExtension.JSON,
            FileExtension.YAML,
            FileExtension.INI,
        }

    @staticmethod
    def from_ext(ext_str: str) -> _Optional["FileExtension"]:
        """Given a file extension, determine what kind of file it is."""

        result = FileExtension.UNKNOWN
        for ext in FileExtension:
            if ext_str in ext.value:
                result = ext
                break
        return None if result is FileExtension.UNKNOWN else result

    @staticmethod
    def from_path(
        path: _Pathlike, maxsplit: int = 1
    ) -> _Optional["FileExtension"]:
        """Get a known file extension for a path, if it exists."""
        return FileExtension.from_ext(get_file_ext(path, maxsplit=maxsplit))

    def apply(self, path: Path) -> Path:
        """Apply this extension's suffix to the given path."""
        return path.with_suffix("." + str(self))

    def candidates(
        self, path: Path, exists_only: bool = False
    ) -> _Iterator[Path]:
        """
        For a given path, iterate over candidate paths that have the suffixes
        for this kind of file extension.
        """
        for ext in self.value:
            path = path.with_suffix(f".{ext}")
            if not exists_only or path.exists():
                yield path

    @staticmethod
    def archive_candidates(
        path: Path, exists_only: bool = False
    ) -> _Iterator[Path]:
        """
        Iterate over all file extensions that could point to an archive file.
        """
        for file_ext in FileExtension:
            if file_ext.is_archive():
                for candidate in file_ext.candidates(path, exists_only):
                    yield candidate

    @staticmethod
    def data_candidates(
        path: Path, exists_only: bool = False
    ) -> _Iterator[Path]:
        """
        Iterate over all file extensions that could point to a data file.
        """
        for file_ext in FileExtension:
            if file_ext.is_data():
                for candidate in file_ext.candidates(path, exists_only):
                    yield candidate


class LoadResult(NamedTuple):
    """
    An encapsulation of the result of loading raw data, the data collected and
    whether or not it succeeded.
    """

    data: dict
    success: bool
    time_ns: int = -1

    def __eq__(self, other: object) -> bool:
        """Don't compare timing when checking equivalence."""
        assert isinstance(other, (LoadResult, tuple))
        return self.data == other[0] and self.success == other[1]

    def require_success(self, path: _Union[Path, str]) -> None:
        """Raise a canonical exception if this result is a failure."""
        assert self.success, f"Couldn't load '{path}'!"


EncodeResult = _Tuple[bool, int]
DataStream = _Union[TextIO, StringIO]
DataDecoder = _Callable[[DataStream, Logger], LoadResult]
DataEncoder = _Callable[[dict, DataStream, Logger], int]

# Only create the interface one so it's not re-created on every read and write
# attempt.
YAML_INTERFACE = YAML(typ="safe")