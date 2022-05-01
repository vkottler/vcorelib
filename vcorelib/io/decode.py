"""
A module implementing various data-file decoders.
"""

# built-in
from configparser import ConfigParser, Error, ExtendedInterpolation
from json import load
from json.decoder import JSONDecodeError
from logging import Logger, getLogger
from typing import Dict as _Dict

# third-party
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError
from tomli import TOMLDecodeError, loads

# internal
from vcorelib.dict import consume
from vcorelib.io.types import DataStream as _DataStream
from vcorelib.io.types import LoadResult
from vcorelib.io.types import YAML_INTERFACE as _YAML_INTERFACE
from vcorelib.math.time import TIMER as _TIMER

_LOG = getLogger(__name__)
_INI_INTERPOLATION = ExtendedInterpolation()


def decode_ini(
    data_file: _DataStream,
    logger: Logger = _LOG,
    **kwargs,
) -> LoadResult:
    """Load INI data from a text stream."""

    data = {}
    loaded = True

    with _TIMER.measure_ns() as token:

        # Allow interpolation when reading by default.
        cparser = ConfigParser(
            interpolation=consume(kwargs, "interpolation", _INI_INTERPOLATION),
            **kwargs,
        )
        try:
            cparser.read_file(data_file)

            for sect_key, section in cparser.items():
                sect_data: _Dict[str, str] = {}
                data[sect_key] = sect_data
                for key, value in section.items():
                    sect_data[key] = value
        except Error as exc:
            loaded = False
            logger.error("config-load error: %s", exc)

    return LoadResult(data, loaded, _TIMER.result(token))


def decode_json(
    data_file: _DataStream,
    logger: Logger = _LOG,
    **kwargs,
) -> LoadResult:
    """Load JSON data from a text stream."""

    data = {}
    loaded = True

    with _TIMER.measure_ns() as token:
        try:
            data = load(data_file, **kwargs)
            if not data:
                data = {}
        except JSONDecodeError as exc:
            loaded = False
            logger.error("json-load error: %s", exc)

    return LoadResult(data, loaded, _TIMER.result(token))


def decode_yaml(
    data_file: _DataStream,
    logger: Logger = _LOG,
    **kwargs,
) -> LoadResult:
    """Load YAML data from a text stream."""

    data = {}
    loaded = True

    with _TIMER.measure_ns() as token:
        try:
            data = _YAML_INTERFACE.load(data_file, **kwargs)
            if not data:
                data = {}
        except (ScannerError, ParserError) as exc:
            loaded = False
            logger.error("yaml-load error: %s", exc)

    return LoadResult(data, loaded, _TIMER.result(token))


def decode_toml(
    data_file: _DataStream,
    logger: Logger = _LOG,
    **kwargs,
) -> LoadResult:
    """Load TOML data from a text stream."""

    data = {}
    loaded = True

    with _TIMER.measure_ns() as token:
        try:
            data = loads(data_file.read(), **kwargs)
        except TOMLDecodeError as exc:
            loaded = False
            logger.error("toml-load error: %s", exc)

    return LoadResult(data, loaded, _TIMER.result(token))
