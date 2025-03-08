"""
Test the 'dict.cache' module.
"""

# built-in
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

# third-party
from pytest import mark

# module under test
from vcorelib.dict.cache import DirectoryCache, FileCache, JsonCache
from vcorelib.io.types import DEFAULT_DATA_EXT


async def cache_test(cache: JsonCache) -> None:
    """Test that writing then reading the cache works."""

    with cache.loaded() as data:
        data["a"] = {"a": 1}
        data["b"] = {"b": 1}
        data["c"] = {"c": 1}

    with cache.loaded() as data:
        assert data["a"] == {"a": 1}
        assert data["b"] == {"b": 1}
        assert data["c"] == {"c": 1}

    async with cache.loaded_async() as data:
        data["a"] = {"a": 2}
        data["b"] = {"b": 2}
        data["c"] = {"c": 2}

    async with cache.loaded_async() as data:
        assert data["a"] == {"a": 2}
        assert data["b"] == {"b": 2}
        assert data["c"] == {"c": 2}


@mark.asyncio
async def test_dict_file_cache_basic():
    """Test that we can use a basic file cache."""

    with NamedTemporaryFile(suffix=f".{DEFAULT_DATA_EXT}") as tfile:
        name = tfile.name

    await cache_test(FileCache(name))
    Path(name).unlink()


@mark.asyncio
async def test_dict_directory_cache_basic():
    """Test that we can use a basic directory cache."""

    with TemporaryDirectory() as tmpdir:
        await cache_test(DirectoryCache(tmpdir))
