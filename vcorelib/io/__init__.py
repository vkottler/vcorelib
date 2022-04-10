"""
A module exposing data-file encoders and decoders.
"""

# built-in
from enum import Enum
import logging
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
from vcorelib.io.types import DataStream as _DataStream
from vcorelib.io.types import EncodeResult as _EncodeResult
from vcorelib.io.types import FileExtension, LoadResult
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import get_file_ext, normalize


class _DataHandle(NamedTuple):
    """A description of a data type."""

    decoder: _DataDecoder
    encoder: _DataEncoder


class DataMapping:
    """
    Map interfaces that read and write data formats to the file extensions
    that most-likely indicate the desire for that kind of format.
    """

    class DataType(Enum):
        """An aggregation of all known data types."""

        INI = _DataHandle(decode_ini, encode_ini)
        JSON = _DataHandle(decode_json, encode_json)
        YAML = _DataHandle(decode_yaml, encode_yaml)
        TOML = _DataHandle(decode_toml, encode_toml)

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


class DataArbiter:
    """
    A class for looking up encode and decode functions for given data types.
    """

    def __init__(
        self,
        logger: logging.Logger = logging.getLogger(__name__),
        encoding: str = "utf-8",
    ) -> None:
        """Initialize a new data arbiter."""
        self.logger = logger
        self.encoding = encoding

    def decoder(self, ext: str) -> _Optional[_DataDecoder]:
        """Look up a decoding routine from a file extension."""

        result = None
        dtype = DataMapping.from_ext_str(ext)
        if dtype is not None:
            result = dtype.value.decoder
        else:
            self.logger.warning("No decoder for '%s'.", ext)
        return result

    def decode_stream(
        self,
        ext: str,
        stream: _DataStream,
        logger: logging.Logger = None,
        **kwargs,
    ) -> LoadResult:
        """Attempt to load data from a text stream."""

        if logger is None:
            logger = self.logger

        result = LoadResult({}, False)
        decoder = self.decoder(ext)
        if decoder is not None:
            result = decoder(stream, logger, **kwargs)
        return result

    def decode(
        self,
        pathlike: _Pathlike,
        logger: logging.Logger = None,
        require_success: bool = False,
        **kwargs,
    ) -> LoadResult:
        """Attempt to load data from a file."""

        result = LoadResult({}, False)
        if logger is None:
            logger = self.logger

        path = normalize(pathlike)
        if path.is_file():
            with path.open(encoding=self.encoding) as path_fd:
                result = self.decode_stream(
                    get_file_ext(path, maxsplit=1), path_fd, logger, **kwargs
                )

        if not result.success:
            logger.error("Failed to decode '%s'.", path)

        # Raise an exception if we expected decoding to succeed.
        if require_success:
            result.require_success(path)

        return result

    def encode_stream(
        self,
        ext: str,
        stream: _DataStream,
        data: dict,
        logger: logging.Logger = None,
        **kwargs,
    ) -> _EncodeResult:
        """Serialize data to an output stream."""

        if logger is None:
            logger = self.logger

        result = False
        encoder = self.encoder(ext)
        time_ns = -1
        if encoder is not None:
            time_ns = encoder(data, stream, logger, **kwargs)
            result = True
        return result, time_ns

    def encode(
        self,
        pathlike: _Pathlike,
        data: dict,
        logger: logging.Logger = None,
        **kwargs,
    ) -> _EncodeResult:
        """Encode data to a file on disk."""

        path = normalize(pathlike)
        with path.open("w", encoding=self.encoding) as path_fd:
            return self.encode_stream(
                get_file_ext(path, maxsplit=1), path_fd, data, logger, **kwargs
            )

    def encoder(self, ext: str) -> _Optional[_DataEncoder]:
        """Look up an encoding routine from a file extension."""

        result = None
        dtype = DataMapping.from_ext_str(ext)
        if dtype is not None:
            result = dtype.value.encoder
        else:
            self.logger.warning("No encoder for '%s'.", ext)
        return result


ARBITER = DataArbiter()
