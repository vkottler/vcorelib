"""
Test the 'dict.cache' module.
"""

# built-in
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

# module under test
from vcorelib.dict.cache import DirectoryCache, FileCache, JsonCache
from vcorelib.io.types import DEFAULT_DATA_EXT


def cache_test(cache: JsonCache) -> None:
    """Test that writing then reading the cache works."""

    with cache.loaded() as data:
        data["a"] = {"a": 1}
        data["b"] = {"b": 1}
        data["c"] = {"c": 1}

    with cache.loaded() as data:
        assert data["a"] == {"a": 1}
        assert data["b"] == {"b": 1}
        assert data["c"] == {"c": 1}


def test_dict_file_cache_basic():
    """Test that we can use a basic file cache."""

    with NamedTemporaryFile(suffix=f".{DEFAULT_DATA_EXT}") as tfile:
        name = tfile.name

    cache_test(FileCache(name))
    Path(name).unlink()


def test_dict_directory_cache_basic():
    """Test that we can use a basic directory cache."""

    with TemporaryDirectory() as tmpdir:
        cache_test(DirectoryCache(tmpdir))
