"""
A module for working with test data.
"""

# built-in
import os
from pathlib import Path

# third-party
import pkg_resources


def resource(
    resource_name: str, valid: bool = True, pkg: str = __name__
) -> Path:
    """Locate the path to a test resource."""

    valid_str = "valid" if valid else "invalid"
    resource_path = os.path.join("data", valid_str, resource_name)
    return Path(pkg_resources.resource_filename(pkg, resource_path))


def get_archives_root(pkg: str = __name__) -> Path:
    """Get the data directory for test archives."""
    path = os.path.join("data", "archives")
    return Path(pkg_resources.resource_filename(pkg, path))
