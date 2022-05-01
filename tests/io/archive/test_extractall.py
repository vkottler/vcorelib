"""
Test the 'extractall' method from the archive module.
"""

# built-in
import os
from pathlib import Path
from tempfile import TemporaryDirectory

# internal
from tests.resources import get_archives_root

# module under test
from vcorelib.io.archive import extractall
from vcorelib.io.definitions import FileExtension


def test_extractall():
    """Test archive-extracting scenarios."""

    root = get_archives_root()
    curr = os.getcwd()
    try:
        # Verify we can extract all of the expected archives.
        for archive in ["tar", "tar.bz2", "tar.gz", "tar.lzma", "zip"]:
            with TemporaryDirectory() as tmpdir:
                assert extractall(Path(root, f"sample.{archive}"), tmpdir)[
                    0
                ], f"Couldn't extract a '{archive}' archive!"

        # Verify we can extract to the working directory.
        with TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            assert extractall(Path(root, "sample.tar"))[0]
            os.chdir(curr)

        # Verify we can't extract an unknown file.
        with TemporaryDirectory() as tmpdir:
            assert not extractall(Path(root, "sample.asdf"), tmpdir)[0]
    finally:
        os.chdir(curr)


def test_has_archive():
    """Verify that we can correctly identify when an archive is present."""

    root = get_archives_root()
    assert FileExtension.has_archive(Path(root, "sample")) is not None
    assert FileExtension.has_archive(Path(root, "not_sample")) is None
