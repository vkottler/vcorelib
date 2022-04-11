"""
A module implementing various data-file encoders.
"""

# built-in
from configparser import ConfigParser
from json import dump
from logging import Logger, getLogger

# third-party
from tomli_w import dumps

# internal
from vcorelib import DEFAULT_INDENT as _DEFAULT_INDENT
from vcorelib.dict import consume
from vcorelib.io.types import DataStream as _DataStream
from vcorelib.io.types import YAML_INTERFACE as _YAML_INTERFACE
from vcorelib.math.time import TIMER as _TIMER

_LOG = getLogger(__name__)


def encode_json(
    configs: dict, ostream: _DataStream, _: Logger = _LOG, **kwargs
) -> int:
    """Write config data as JSON to the output stream."""

    with _TIMER.measure_ns() as token:
        # Normalize arguments with some defaults.
        dump(
            configs,
            ostream,
            indent=consume(kwargs, "indent", _DEFAULT_INDENT),
            sort_keys=consume(kwargs, "sort_keys", True),
            **kwargs
        )
    return _TIMER.result(token)


def encode_yaml(
    configs: dict, ostream: _DataStream, _: Logger = _LOG, **kwargs
) -> int:
    """Write config data as YAML to the output stream."""

    with _TIMER.measure_ns() as token:
        _YAML_INTERFACE.dump(configs, ostream, **kwargs)
    return _TIMER.result(token)


def encode_ini(
    configs: dict, ostream: _DataStream, _: Logger = _LOG, **kwargs
) -> int:
    """Write config data as INI to the output stream."""

    with _TIMER.measure_ns() as token:
        cparser = ConfigParser(
            interpolation=consume(kwargs, "interpolation"), **kwargs
        )
        cparser.read_dict(configs)
        cparser.write(ostream)
    return _TIMER.result(token)


def encode_toml(
    configs: dict, ostream: _DataStream, _: Logger = _LOG, **kwargs
) -> int:
    """Write config data as TOML to the output stream."""

    with _TIMER.measure_ns() as token:
        ostream.write(dumps(configs, **kwargs))
    return _TIMER.result(token)
