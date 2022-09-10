"""
Test the 'io.abc' module.
"""

# built-in
from pathlib import Path
from typing import TextIO as _TextIO

# module under test
from vcorelib.io.abc import FileEntity


def test_io_file_entity_basic():
    """Test basic interactions with a file entity."""

    class Sample(FileEntity):
        """Sample implementation."""

        def to_stream(self, stream: _TextIO, **kwargs) -> None:
            """Write this object to a text stream."""
            print(stream)

    test = Sample("test.txt")
    assert test.default_location() == Path("test.txt")
