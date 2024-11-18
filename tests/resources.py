"""
A module for working with test data.
"""

# built-in
from functools import cache
from os.path import join
from pathlib import Path

# internal
from vcorelib.io import DEFAULT_INCLUDES_KEY
from vcorelib.schemas.base import SchemaMap
from vcorelib.schemas.json import JsonSchemaMap


def resource(resource_name: str, *parts: str, valid: bool = True) -> Path:
    """Locate the path to a test resource."""

    return Path(__file__).parent.joinpath(
        "data", "valid" if valid else "invalid", resource_name, *parts
    )


def get_archives_root() -> Path:
    """Get the data directory for test archives."""
    return Path(__file__).parent.joinpath("data", "archives")


@cache
def get_test_schemas() -> SchemaMap:
    """Get schemas stored in test data."""

    return JsonSchemaMap.from_package(
        "tests",
        package_subdir=join("data", "valid"),
        includes_key=DEFAULT_INCLUDES_KEY,
    )
