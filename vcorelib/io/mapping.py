"""
A module mapping file extensions to encoders and decoders.
"""

# built-in
from enum import Enum
from typing import NamedTuple
from typing import Optional as _Optional

# internal
from vcorelib.io.decode import (
    decode_ini,
    decode_json,
    decode_toml,
    decode_yaml,
)
from vcorelib.io.encode import (
    encode_ini,
    encode_json,
    encode_toml,
    encode_yaml,
)
from vcorelib.io.types import DataDecoder as _DataDecoder
from vcorelib.io.types import DataEncoder as _DataEncoder
from vcorelib.io.types import FileExtension


class DataHandle(NamedTuple):
    """A description of a data type."""

    decoder: _DataDecoder
    encoder: _DataEncoder


class DataType(Enum):
    """An aggregation of all known data types."""

    INI = DataHandle(decode_ini, encode_ini)
    JSON = DataHandle(decode_json, encode_json)
    YAML = DataHandle(decode_yaml, encode_yaml)
    TOML = DataHandle(decode_toml, encode_toml)


class DataMapping:
    """
    Map interfaces that read and write data formats to the file extensions
    that most-likely indicate the desire for that kind of format.
    """

    mapping = {
        FileExtension.INI: DataType.INI,
        FileExtension.JSON: DataType.JSON,
        FileExtension.YAML: DataType.YAML,
        FileExtension.TOML: DataType.TOML,
    }

    @staticmethod
    def from_ext(ext: FileExtension = None) -> _Optional["DataType"]:
        """Map a file extension to a data type."""

        if ext is None:
            ext = FileExtension.UNKNOWN
        return DataMapping.mapping.get(ext)

    @staticmethod
    def from_ext_str(ext: str) -> _Optional["DataType"]:
        """Get a data type from a file-extension string."""
        return DataMapping.from_ext(FileExtension.from_ext(ext))
