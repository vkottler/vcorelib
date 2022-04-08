"""
A module implementing various data-file encoders.
"""

# built-in
from configparser import ConfigParser
import json
from logging import Logger, getLogger
from time import perf_counter_ns

# third-party
import tomli_w

# internal
from vcorelib import DEFAULT_INDENT
from vcorelib.dict import consume
from vcorelib.io.types import YAML_INTERFACE, DataStream

LOG = getLogger(__name__)


def encode_json(
    configs: dict, ostream: DataStream, _: Logger = LOG, **kwargs
) -> int:
    """Write config data as JSON to the output stream."""

    start = perf_counter_ns()

    # Normalize arguments with some defaults.
    json.dump(
        configs,
        ostream,
        indent=consume(kwargs, "indent", DEFAULT_INDENT),
        sort_keys=consume(kwargs, "sort_keys", True),
        **kwargs
    )
    return perf_counter_ns() - start


def encode_yaml(
    configs: dict, ostream: DataStream, _: Logger = LOG, **kwargs
) -> int:
    """Write config data as YAML to the output stream."""

    start = perf_counter_ns()
    YAML_INTERFACE.dump(configs, ostream, **kwargs)
    return perf_counter_ns() - start


def encode_ini(
    configs: dict, ostream: DataStream, _: Logger = LOG, **kwargs
) -> int:
    """Write config data as INI to the output stream."""

    start = perf_counter_ns()
    cparser = ConfigParser(
        interpolation=consume(kwargs, "interpolation"), **kwargs
    )
    cparser.read_dict(configs)
    cparser.write(ostream)
    return perf_counter_ns() - start


def encode_toml(
    configs: dict, ostream: DataStream, _: Logger = LOG, **kwargs
) -> int:
    """Write config data as TOML to the output stream."""

    start = perf_counter_ns()
    ostream.write(tomli_w.dumps(configs, **kwargs))
    return perf_counter_ns() - start
