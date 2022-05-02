"""
datazen - Tests for the 'paths' API.
"""

from os import sep

# built-in
from pathlib import Path

# internal
from tests.resources import resource

# module under test
from vcorelib.io.types import FileExtension
from vcorelib.paths import file_md5_hex, find_file, get_file_name, str_md5_hex


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


def test_md5_hex():
    """Test that various md5 functions provide the correct results."""

    assert str_md5_hex("test") == "098f6bcd4621d373cade4e832627b4f6"
    assert (
        file_md5_hex(resource("test.txt"))
        == "d8e8fca2dc0f896fd7cb4cb0031ba249"
    )


def test_find_file():
    """Test that we can correctly locate files."""

    assert find_file(Path(sep), "a", "b", "c") is None
    assert find_file(Path(__file__).resolve())
    assert find_file("test.txt", include_cwd=True) is None
