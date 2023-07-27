"""
Test the 'paths.hashing' module.
"""

# internal
from tests.resources import get_archives_root, resource

# module under test
from vcorelib.paths import create_hex_digest, validate_hex_digest


def test_create_hex_digest_basic():
    """Test that we can create a hex-digest file."""

    create_hex_digest(get_archives_root(), "test").unlink()


def test_validate_hex_digest_basic():
    """Test that we can validate hex-digest files."""

    root = get_archives_root()

    validate_hex_digest(resource("test.md5sum"), root=root)
    validate_hex_digest(resource("test.sha256sum"), root=root)
