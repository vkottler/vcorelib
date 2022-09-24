"""
A module exposing data-file encoders and decoders.
"""

# built-in
from contextlib import contextmanager as _contextmanager
from enum import Enum
import logging
from pathlib import Path
from typing import Any as _Any
from typing import Callable as _Callable
from typing import Iterator as _Iterator
from typing import NamedTuple
from typing import Optional as _Optional
from typing import cast as _cast

# internal
from vcorelib import DEFAULT_ENCODING as _DEFAULT_ENCODING
from vcorelib.dict import GenericStrDict as _GenericStrDict
from vcorelib.dict import consume, merge
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
from vcorelib.io.types import DEFAULT_DATA_EXT as _DEFAULT_DATA_EXT
from vcorelib.io.types import DataDecoder as _DataDecoder
from vcorelib.io.types import DataEncoder as _DataEncoder
from vcorelib.io.types import DataStream as _DataStream
from vcorelib.io.types import EncodeResult as _EncodeResult
from vcorelib.io.types import FileExtension
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue
from vcorelib.io.types import LoadResult
from vcorelib.io.types import StreamProcessor as _StreamProcessor
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import find_file, get_file_ext, get_file_name, normalize


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
        encoding: str = _DEFAULT_ENCODING,
    ) -> None:
        """Initialize a new data arbiter."""
        self.logger = logger
        self.encoding = encoding

    def _decoder(self, ext: str) -> _Optional[_DataDecoder]:
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
        decoder = self._decoder(ext)
        if decoder is not None:
            result = decoder(stream, logger, **kwargs)
        return result

    def decode(
        self,
        pathlike: _Pathlike,
        logger: logging.Logger = None,
        require_success: bool = False,
        includes_key: _Any = None,
        preprocessor: _StreamProcessor = None,
        maxsplit: int = 1,
        **kwargs,
    ) -> LoadResult:
        """Attempt to load data from a file."""

        result = LoadResult({}, False)
        if logger is None:
            logger = self.logger

        path = normalize(pathlike)
        if path.is_file():
            with path.open(encoding=self.encoding) as path_fd:
                # Preprocess the stream if specified. This can be useful for
                # external code to treat data files as templates.
                result = self.decode_stream(
                    get_file_ext(path, maxsplit=maxsplit),
                    preprocessor(path_fd)
                    if preprocessor is not None
                    else path_fd,
                    logger,
                    **kwargs,
                )

                # Resolve includes if necessary.
                if includes_key is not None:
                    for include in consume(result.data, includes_key, []):
                        # Load the included file.
                        result = result.merge(
                            self.decode(
                                find_file(include, relative_to=path),
                                logger,
                                require_success,
                                includes_key,
                                **kwargs,
                            )
                        )

        if not result.success:
            logger.error("Failed to decode '%s'.", path)

        # Raise an exception if we expected decoding to succeed.
        if require_success:
            result.require_success(path)

        return result

    def decode_directory(
        self,
        pathlike: _Pathlike,
        logger: logging.Logger = None,
        require_success: bool = False,
        path_filter: _Callable[[Path], bool] = None,
        recurse: bool = False,
        **kwargs,
    ) -> LoadResult:
        """
        Attempt to decode data files in a directory. Assigns data loaded from
        each file to a key, returns whether or not any files failed to load
        and the cumulative time that each file-load took.
        """

        data: _JsonObject = {}
        path = normalize(pathlike)
        errors = 0
        load_time = 0

        for child in filter(
            path_filter if path_filter is not None else lambda _: True,
            path.iterdir(),
        ):
            load = None
            if child.is_file():
                load = self.decode(child, logger, require_success, **kwargs)
            elif recurse and child.is_dir():
                load = self.decode_directory(
                    child,
                    logger,
                    require_success,
                    path_filter,
                    recurse,
                    **kwargs,
                )

            if load is not None:
                if load.success:
                    key = get_file_name(child)
                    if key:
                        data[key] = _cast(_JsonValue, load.data)
                    else:
                        data = merge(
                            data,
                            load.data,
                            expect_overwrite=kwargs.get(
                                "expect_overwrite", False
                            ),
                            logger=logger,
                        )
                errors += int(not load.success)
                if load.time_ns:
                    load_time += load.time_ns

        return LoadResult(data, errors == 0, load_time)

    def encode_stream(
        self,
        ext: str,
        stream: _DataStream,
        data: _JsonObject,
        logger: logging.Logger = None,
        **kwargs,
    ) -> _EncodeResult:
        """Serialize data to an output stream."""

        if logger is None:
            logger = self.logger

        result = False
        encoder = self._encoder(ext)
        time_ns = -1
        if encoder is not None:
            time_ns = encoder(data, stream, logger, **kwargs)
            result = True
        return result, time_ns

    def encode(
        self,
        pathlike: _Pathlike,
        data: _JsonObject,
        logger: logging.Logger = None,
        maxsplit: int = 1,
        **kwargs,
    ) -> _EncodeResult:
        """Encode data to a file on disk."""

        path = normalize(pathlike)
        with path.open("w", encoding=self.encoding) as path_fd:
            return self.encode_stream(
                get_file_ext(path, maxsplit=maxsplit),
                path_fd,
                data,
                logger,
                **kwargs,
            )

    def encode_directory(
        self,
        pathlike: _Pathlike,
        data: _JsonObject,
        ext: str = _DEFAULT_DATA_EXT,
        logger: logging.Logger = None,
        **kwargs,
    ) -> _EncodeResult:
        """
        Encode data to a directory where every key becomes a file with the
        provided extension. The encoding scheme is implied by the extension.
        """

        success = True
        time_ns = 0
        root = normalize(pathlike)

        for key, item in data.items():
            result = self.encode(
                root.joinpath(f"{key}.{ext}"),
                _cast(_JsonObject, item),
                logger,
                **kwargs,
            )
            success &= result[0]
            if result[1]:
                time_ns += result[1]

        return success, time_ns

    def _encoder(self, ext: str) -> _Optional[_DataEncoder]:
        """Look up an encoding routine from a file extension."""

        result = None
        dtype = DataMapping.from_ext_str(ext)
        if dtype is not None:
            result = dtype.value.encoder
        else:
            self.logger.warning("No encoder for '%s'.", ext)
        return result

    @_contextmanager
    def object_file_context(
        self,
        pathlike: _Pathlike,
        decode_kwargs: _GenericStrDict = None,
        encode_kwargs: _GenericStrDict = None,
    ) -> _Iterator[_JsonObject]:
        """
        Provide data loaded from a file as a context so that it's written back
        when the context ends.
        """
        if decode_kwargs is None:
            decode_kwargs = {}
        if encode_kwargs is None:
            encode_kwargs = {}
        data = self.decode(pathlike, **decode_kwargs).data
        yield data
        self.encode(pathlike, data, **encode_kwargs)

    @_contextmanager
    def object_directory_context(
        self,
        pathlike: _Pathlike,
        decode_kwargs: _GenericStrDict = None,
        encode_kwargs: _GenericStrDict = None,
    ) -> _Iterator[_JsonObject]:
        """Provide a loaded directory as a context."""

        if decode_kwargs is None:
            decode_kwargs = {}
        if encode_kwargs is None:
            encode_kwargs = {}

        # Make sure the directory exists, since we would create it anyway.
        path = normalize(pathlike)
        path.mkdir(parents=True, exist_ok=True)

        data = self.decode_directory(path, **decode_kwargs).data
        yield data
        self.encode_directory(
            pathlike,
            data,
            **encode_kwargs,
        )


ARBITER = DataArbiter()
