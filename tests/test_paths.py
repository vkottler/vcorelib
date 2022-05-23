"""
datazen - Tests for the 'paths' API.
"""

# built-in
from os import linesep, sep
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep

# internal
from tests.resources import resource

# module under test
from vcorelib.io.types import FileExtension
from vcorelib.paths import (
    file_md5_hex,
    find_file,
    get_file_name,
    modified_after,
    modified_ns,
    stats,
    str_md5_hex,
)


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


def test_file_stats_basic():
    """Test that we can obtain basic file statistics."""

    path = resource("test.txt")
    assert stats(path) is not None
    assert modified_ns(path)

    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        first_file = tmpdir.joinpath("test1.txt")
        second_file = tmpdir.joinpath("test2.txt")

        # Write to the first file.
        with first_file.open("w", encoding="utf-8") as path_fd:
            path_fd.write("test")
            path_fd.write(linesep)
            path_fd.flush()

        # Wait some amount so that the second file is modified after the first.
        sleep(0.01)

        # Write to the second file.
        with second_file.open("w", encoding="utf-8") as path_fd:
            for i in range(1000):
                path_fd.write(str(i))
                path_fd.write(linesep)
            path_fd.flush()

        assert modified_after(first_file, [second_file])
        assert not modified_after(second_file, [first_file])
        assert modified_after(tmpdir.joinpath("test3.txt"), [first_file])
        assert modified_after(tmpdir.joinpath("test4.txt"), [second_file])
