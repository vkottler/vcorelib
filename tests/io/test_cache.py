"""
Test the 'FlatDirectoryCache' class and 'io.cache' module.
"""

# built-in
import logging
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

# module under test
from vcorelib.io.cache import FlatDirectoryCache

# internal
from tests.resources import get_archives_root, resource


def test_directory_cache_basic():
    """Test basic loading and saving functions of the directory cache."""

    # Load data.
    logger = logging.getLogger(__name__)
    cache = FlatDirectoryCache(
        resource("simple_decode").joinpath("json"), logger=logger
    )
    cache.changed = True
    assert cache
    assert all(x in cache for x in "abc")

    # Save data, verify saved data on subsequent load.
    with TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        cache.save(tmpdir, logger=logger)
        new_cache = FlatDirectoryCache(tmpdir, logger=logger)
        new_cache.changed = True
        assert new_cache == cache
        new_cache.save(logger=logger)
        assert new_cache == new_cache.load()

        # Clean the cache and verify the next load contains no data.
        new_cache.clean(logger=logger)
        new_cache = FlatDirectoryCache(tmpdir, logger=logger)
        assert not new_cache
        tmpdir.mkdir()


def test_directory_cache_archive_load():
    """Test that we can load a cache, when only an archive for it exists."""

    logger = logging.getLogger(__name__)
    root = get_archives_root()
    for archive in ["tar", "tar.bz2", "tar.gz", "tar.lzma", "zip"]:
        archive_name = f"sample.{archive}"
        path = Path(root, archive_name)

        with TemporaryDirectory() as tmp:
            # Copy the archive to the expected location.
            shutil.copy(path, Path(tmp, archive_name))

            # Load the cache.
            cache = FlatDirectoryCache(Path(tmp, "sample"), logger=logger)
            assert cache
            assert all(x in cache for x in "abc")

            # Verify that we can clean the cache.
            cache.save(archive=True)
            cache.clean()


def test_directory_cache_save_archive():
    """Test that we can create a cache archive and load from it."""

    logger = logging.getLogger(__name__)
    cache = FlatDirectoryCache(
        resource("simple_decode").joinpath("json"), logger=logger
    )
    assert cache

    with TemporaryDirectory() as tmp:
        path = Path(tmp, "test")
        cache.changed = True
        cache.save(path, logger, archive=True)

        # Remove the non-archived data.
        shutil.rmtree(path)
        assert Path(tmp, f"test.{cache.archive_encoding}").is_file()

        # Create a new cache, only load from the archive.
        new_cache = FlatDirectoryCache(path, logger=logger)
        assert new_cache.data == cache.data
