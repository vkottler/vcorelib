"""
A module for working with test data.
"""

# built-in
from os.path import join
from pathlib import Path
from sys import platform, version

# internal
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


def get_test_schemas() -> SchemaMap:
    """Get schemas stored in test data."""
    return JsonSchemaMap.from_package(
        "tests", package_subdir=join("data", "valid")
    )


def skip_archive(kind: str) -> bool:
    """
    Whether or not to skip a particular kind of archive when testing.
    Currently, bz2 extraction on Python 3.7 on macos is not working.
    """
    return "bz2" in kind and platform == "darwin" and version.startswith("3.7")
