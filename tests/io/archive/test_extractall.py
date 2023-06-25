"""
Test the 'extractall' method from the archive module.
"""

# built-in
from pathlib import Path
from tempfile import TemporaryDirectory

# internal
from tests.resources import get_archives_root

# module under test
from vcorelib.io.archive import extractall
from vcorelib.io.types import FileExtension
from vcorelib.paths.context import in_dir


def test_extractall():
    """Test archive-extracting scenarios."""

    root = get_archives_root()
    curr = Path()

    # Verify we can't extract an unknown file.
    with TemporaryDirectory() as tmpdir:
        assert not extractall(root.joinpath("sample.asdf"), dst=tmpdir)[0]

    with in_dir(curr):
        fail = None
        # Verify we can extract all of the expected archives.
        for archive in ["tar", "tar.bz2", "tar.gz", "tar.lzma", "zip"]:
            with TemporaryDirectory() as tmpdir:
                if not extractall(
                    root.joinpath(f"sample.{archive}"), dst=tmpdir
                )[0]:
                    fail = f"Couldn't extract a '{archive}' archive!"
                    break

        assert fail is None, fail

    # Verify we can extract to the working directory.
    with TemporaryDirectory() as tmpdir:
        with in_dir(tmpdir):
            assert extractall(root.joinpath("sample.tar"))[0]


def test_has_archive():
    """Verify that we can correctly identify when an archive is present."""

    root = get_archives_root()
    assert FileExtension.has_archive(Path(root, "sample")) is not None
    assert FileExtension.has_archive(Path(root, "not_sample")) is None
