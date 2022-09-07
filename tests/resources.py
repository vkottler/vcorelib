"""
A module for working with test data.
"""

# built-in
from os.path import join
from pathlib import Path

# third-party
import pkg_resources

# internal
from vcorelib.schemas import JsonSchemaMap
from vcorelib.schemas.base import SchemaMap


def resource(
    resource_name: str, *parts: str, valid: bool = True, pkg: str = __name__
) -> Path:
    """Locate the path to a test resource."""

    return Path(
        pkg_resources.resource_filename(
            pkg,
            join(
                "data", "valid" if valid else "invalid", resource_name, *parts
            ),
        )
    )


def get_archives_root(pkg: str = __name__) -> Path:
    """Get the data directory for test archives."""
    return Path(pkg_resources.resource_filename(pkg, join("data", "archives")))


def test_schemas() -> SchemaMap:
    """Get schemas stored in test data."""
    return JsonSchemaMap.from_package(
        "tests", package_subdir=join("data", "valid")
    )
