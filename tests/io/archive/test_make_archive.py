"""
Test the 'make_archive' method from the archive module.
"""

# built-in
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

# internal
from tests.resources import get_archives_root, skip_archive

# module under test
from vcorelib.io.archive import make_archive


def test_make_archive():
    """Test that archives can be created."""

    archive_data = Path(get_archives_root(), "sample")
    with TemporaryDirectory() as tmpdir:
        # Copy sample data into the temporary directory.
        shutil.copytree(archive_data, Path(tmpdir, "sample"))

        # Perform testing while inside the temporary directory.
        curr = os.getcwd()
        try:
            os.chdir(tmpdir)

            src = Path("sample")

            # Test expected successes.
            assert make_archive(src)[0] is not None
            for archive in ["tar", "tar.bz2", "tar.lzma", "tar.xz", "zip"]:
                if skip_archive(archive):
                    continue
                assert make_archive(src, archive)[0] is not None

            with TemporaryDirectory() as tmpdir_new:
                assert (
                    make_archive(src, dst_dir=Path(tmpdir_new))[0] is not None
                )

            # Test expected failures.
            assert make_archive(Path("not_sample"))[0] is None
            assert make_archive(src, "tar.asdf")[0] is None
        finally:
            os.chdir(curr)
