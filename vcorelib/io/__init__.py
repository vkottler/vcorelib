"""
A module exposing data-file encoders and decoders.
"""

# internal
from vcorelib.io.abc import FileEntity, Serializable
from vcorelib.io.arbiter import ARBITER, DataArbiter
from vcorelib.io.fifo import ByteFifo
from vcorelib.io.file_writer import IndentedFileWriter
from vcorelib.io.types import (
    DataDecoder,
    DataEncoder,
    DataStream,
    EncodeResult,
    FileExtension,
    JsonArray,
    JsonObject,
    JsonPrimitive,
    JsonValue,
    LoadResult,
    StreamProcessor,
)

DEFAULT_INCLUDES_KEY = "includes"

__all__ = [
    "DataArbiter",
    "ARBITER",
    "JsonPrimitive",
    "JsonValue",
    "JsonArray",
    "JsonObject",
    "FileExtension",
    "LoadResult",
    "EncodeResult",
    "DataStream",
    "StreamProcessor",
    "DataDecoder",
    "DataEncoder",
    "Serializable",
    "FileEntity",
    "DEFAULT_INCLUDES_KEY",
    "IndentedFileWriter",
    "ByteFifo",
]
