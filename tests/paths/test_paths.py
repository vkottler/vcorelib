"""
Tests for the 'paths' module.
"""

# built-in
from logging import getLogger
from os import linesep, sep
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep

# internal
from tests.resources import get_archives_root, resource

# module under test
from vcorelib import DEFAULT_ENCODING
from vcorelib.io.types import FileExtension
from vcorelib.paths import (
    file_hash_hex,
    file_md5_hex,
    find_file,
    get_file_name,
    modified_after,
    modified_ns,
    normalize,
    prune_empty_directories,
    rel,
    set_exec_flags,
    stats,
    str_hash_hex,
    str_md5_hex,
)
from vcorelib.paths.context import as_path, in_dir, tempfile
from vcorelib.platform import is_windows


def test_file_name_ext():
    """Test various file name to extention conversions."""

    assert FileExtension.from_path("test") is None

    assert FileExtension.from_path("json") is FileExtension.JSON
    assert FileExtension.from_path("a.json") is FileExtension.JSON
    assert FileExtension.from_path("a.b.json") is not FileExtension.JSON
    ext = FileExtension.from_path("a.json")
    assert ext is not None and ext.is_data()

    assert FileExtension.from_path("a.tar") is FileExtension.TAR
    assert FileExtension.from_path("a.tar.gz") is FileExtension.TAR
    assert FileExtension.from_path("a.tar.bz2") is FileExtension.TAR
    ext = FileExtension.from_path("a.tar.gz")
    assert ext is not None and ext.is_archive()


def test_file_name():
    """Test that file name determinism is correct."""

    assert get_file_name("a/b/c.yaml") == "c"
    assert get_file_name("a/b/c") == "c"


def test_md5_hex():
    """Test that various md5 functions provide the correct results."""

    assert str_md5_hex("test") == "098f6bcd4621d373cade4e832627b4f6"

    # This difference is caused by the newline translation done by git
    # (by default on Windows). It would be better to check the sum of a
    # file that's not text.
    expect = (
        "9f06243abcb89c70e0c331c61d871fa7"
        if is_windows()
        else "d8e8fca2dc0f896fd7cb4cb0031ba249"
    )
    assert file_md5_hex(resource("test.txt")) == expect

    # Verify we can assert that files exist.
    assert normalize(resource("scripts"), "test.py", require=True)


def test_hash_hex():
    """Test various hashing wrapper methods."""

    assert (
        str_hash_hex("test")
        == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    )
    assert (
        file_hash_hex(get_archives_root().joinpath("sample.tar.gz"))
        == "e160107656e11b3fcf26bb7db9cccfcba7ab3ba20ceb7c7aeadaee2ca6c077b7"
    )


def test_find_file():
    """Test that we can correctly locate files."""

    logger = getLogger(__name__)

    assert find_file(Path(sep), "a", "b", "c", logger=logger) is None
    assert find_file(Path(__file__).resolve(), logger=logger)
    assert find_file("test.txt", include_cwd=True, logger=logger) is None

    # Verify that we can load package resources.
    assert find_file("valid", package="tests", logger=logger)
    assert find_file("valid", "scripts", package="tests", logger=logger)
    assert find_file("valid", "test.txt", package="tests", logger=logger)
    assert (
        find_file(
            "valid",
            "a",
            package="tests",
            search_paths=[Path(sep)],
            logger=logger,
        )
        is None
    )
    assert find_file("resource", package="fake_package", logger=logger) is None


def test_file_stats_basic():
    """Test that we can obtain basic file statistics."""

    path = resource("test.txt")
    assert stats(path) is not None
    assert modified_ns(path)

    with TemporaryDirectory() as _tmpdir:
        tmpdir = Path(_tmpdir)
        first_file = tmpdir.joinpath("test1.txt")
        second_file = tmpdir.joinpath("test2.txt")

        # Write to the first file.
        with first_file.open("w", encoding="utf-8") as path_fd:
            path_fd.write("test")
            path_fd.write(linesep)
            path_fd.flush()

        set_exec_flags(first_file)

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

        # Open both files for reading and then perform the same verification.
        with first_file.open(encoding="utf-8") as path_fd:
            sleep(0.01)
            assert path_fd.read()
        with second_file.open(encoding="utf-8") as path_fd:
            sleep(0.01)
            assert path_fd.read()

        assert modified_after(first_file, [second_file])
        assert not modified_after(second_file, [first_file])

        assert modified_after(tmpdir.joinpath("test3.txt"), [first_file])
        assert modified_after(tmpdir.joinpath("test4.txt"), [second_file])


def test_prune_empty_directories():
    """Test pruning empty directories."""

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir, "test")
        root.mkdir()

        for subdir in "abc":
            root.joinpath(subdir).mkdir()
            root.joinpath(subdir, "subdir").mkdir()
            root.joinpath(subdir, "subdir", "subdir2").mkdir()

        prune_empty_directories(root)

        # Confirm directory is gone.
        assert not root.is_dir()


def test_paths_in_dir():
    """Test that we can change directories as a context manager."""

    with TemporaryDirectory() as tmpdir:
        with in_dir(tmpdir, makedirs=True):
            assert Path.cwd().samefile(Path(tmpdir))


def test_paths_tempfile():
    """Test that we can create a temporary file."""

    with tempfile() as temp:
        path = temp
    assert not path.is_file()


def test_paths_rel_basic():
    """Test the behavior of the relative-pather."""

    assert str(rel(Path("test.txt").resolve())) == "test.txt"


def test_as_path_basic():
    """Test converting data to an on-disk path."""

    msg = "Hello, world!"
    with as_path(msg) as path:
        # SA bug (path should be detected as Path instance).
        path = Path(path)
        with path.open("r", encoding=DEFAULT_ENCODING) as path_fd:
            assert path_fd.read() == msg

    assert not path.exists()
