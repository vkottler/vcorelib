"""
Test the 'paths.hashing' module.
"""

# internal
from tests.resources import get_archives_root

# module under test
from vcorelib.paths import create_hex_digest


def test_create_hex_digest_basic():
    """Test that we can create a hex-digest file."""

    create_hex_digest(get_archives_root(), "test").unlink()
