"""
datazen - Tests for the 'paths' API.
"""

# module under test
from vcorelib.io.types import FileExtension
from vcorelib.paths import get_file_name


def test_file_name_ext():
    """Test various file name to extention conversions."""

    assert FileExtension.from_path("test") is None

    assert FileExtension.from_path("json") is FileExtension.JSON
    assert FileExtension.from_path("a.json") is FileExtension.JSON
    assert FileExtension.from_path("a.b.json") is not FileExtension.JSON
    assert FileExtension.from_path("a.json").is_data()

    assert FileExtension.from_path("a.tar") is FileExtension.TAR
    assert FileExtension.from_path("a.tar.gz") is FileExtension.TAR
    assert FileExtension.from_path("a.tar.bz2") is FileExtension.TAR
    assert FileExtension.from_path("a.tar.gz").is_archive()


def test_file_name():
    """Test that file name determinism is correct."""

    assert get_file_name("a/b/c.yaml") == "c"
    assert get_file_name("a/b/c") == "c"
