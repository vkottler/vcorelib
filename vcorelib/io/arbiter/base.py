"""
A module exposing data-file encoders and decoders.
"""

# built-in
import logging
from typing import Optional as _Optional

# internal
from vcorelib import DEFAULT_ENCODING as _DEFAULT_ENCODING
from vcorelib.dict import MergeStrategy, consume
from vcorelib.io.mapping import DataMapping
from vcorelib.io.types import DataDecoder as _DataDecoder
from vcorelib.io.types import DataEncoder as _DataEncoder
from vcorelib.io.types import DataStream as _DataStream
from vcorelib.io.types import EncodeResult as _EncodeResult
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import LoadResult
from vcorelib.io.types import StreamProcessor as _StreamProcessor
from vcorelib.logging import LoggerType
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import find_file, get_file_ext, normalize


class DataArbiterBase:
    """
    A class for looking up encode and decode functions for given data types.
    """

    def __init__(
        self,
        logger: LoggerType = logging.getLogger(__name__),
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
        logger: LoggerType = None,
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
        logger: LoggerType = None,
        require_success: bool = False,
        includes_key: str = None,
        preprocessor: _StreamProcessor = None,
        maxsplit: int = 1,
        expect_overwrite: bool = False,
        strategy: MergeStrategy = MergeStrategy.RECURSIVE,
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
                                require_success=require_success,
                                includes_key=includes_key,
                                **kwargs,
                            ),
                            expect_overwrite=expect_overwrite,
                            logger=logger,
                            strategy=strategy,
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
        data: _JsonObject,
        logger: LoggerType = None,
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
        logger: LoggerType = None,
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

    def _encoder(self, ext: str) -> _Optional[_DataEncoder]:
        """Look up an encoding routine from a file extension."""

        result = None
        dtype = DataMapping.from_ext_str(ext)
        if dtype is not None:
            result = dtype.value.encoder
        else:
            self.logger.warning("No encoder for '%s'.", ext)
        return result
