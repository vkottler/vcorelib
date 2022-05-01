"""
Test the 'io.types' module.
"""

# built-in
from pathlib import Path

# internal
from tests.resources import resource

# module under test
from vcorelib.io.types import FileExtension, LoadResult


def test_data_files_simple():
    """Test that we can find files that contain data."""

    assert LoadResult({}, False) == LoadResult({}, False)

    root = resource("simple_decode").joinpath("json")
    for path in "abc":
        candidates = list(
            FileExtension.data_candidates(Path(root, path), True)
        )
        assert len(candidates) > 0

        candidates = list(
            FileExtension.data_candidates(Path(root, f"{path}.txt"), True)
        )
        assert len(candidates) > 0
