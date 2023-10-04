"""
A module implementing various data-file encoders.
"""

# built-in
from configparser import ConfigParser
from json import dump
from logging import getLogger
from os import linesep
from typing import cast as _cast

# third-party
from ruamel.yaml import YAML
from tomli_w import dumps

# internal
from vcorelib import DEFAULT_INDENT as _DEFAULT_INDENT
from vcorelib.dict import GenericStrDict as _GenericStrDict
from vcorelib.dict import consume
from vcorelib.io.types import DataStream as _DataStream
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.logging import LoggerType
from vcorelib.math.time import TIMER as _TIMER

_LOG = getLogger(__name__)


def encode_json(
    configs: _JsonObject, ostream: _DataStream, _: LoggerType = _LOG, **kwargs
) -> int:
    """Write config data as JSON to the output stream."""

    with _TIMER.measure_ns() as token:
        # Normalize arguments with some defaults.
        dump(
            configs,
            ostream,
            indent=consume(kwargs, "indent", _DEFAULT_INDENT),
            sort_keys=consume(kwargs, "sort_keys", True),
            **kwargs,
        )
    return _TIMER.result(token)


def encode_yaml(
    configs: _JsonObject,
    ostream: _DataStream,
    _: LoggerType = _LOG,
    sequence: int = 4,
    offset: int = 2,
    mapping: int = 2,
    document_start: bool = True,
    **kwargs,
) -> int:
    """Write config data as YAML to the output stream."""

    with _TIMER.measure_ns() as token:
        with YAML(output=ostream) as yaml:
            yaml.indent(sequence=sequence, offset=offset, mapping=mapping)
            if document_start:
                ostream.write("---" + linesep)
            yaml.dump(configs, **kwargs)
    return _TIMER.result(token)


def encode_ini(
    configs: _JsonObject, ostream: _DataStream, _: LoggerType = _LOG, **kwargs
) -> int:
    """Write config data as INI to the output stream."""

    with _TIMER.measure_ns() as token:
        cparser = ConfigParser(
            interpolation=consume(kwargs, "interpolation"), **kwargs
        )
        cparser.read_dict(_cast(_GenericStrDict, configs))
        cparser.write(ostream)
    return _TIMER.result(token)


def encode_toml(
    configs: _JsonObject, ostream: _DataStream, _: LoggerType = _LOG, **kwargs
) -> int:
    """Write config data as TOML to the output stream."""

    with _TIMER.measure_ns() as token:
        ostream.write(dumps(configs, **kwargs))
    return _TIMER.result(token)
