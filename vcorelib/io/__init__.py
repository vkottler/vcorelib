"""
A module exposing data-file encoders and decoders.
"""

# internal
from vcorelib.io.abc import FileEntity, Serializable
from vcorelib.io.arbiter import ARBITER, DataArbiter
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
]
