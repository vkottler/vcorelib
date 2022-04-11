"""
Test the 'DataArbiter' class.
"""

# built-in
from contextlib import suppress
from pathlib import Path

# internal
from tests.resources import resource

# module under test
from vcorelib.io import ARBITER, DataMapping


def test_arbiter_decode_basic():
    """Verify that we can load data of every file type."""

    base = resource("simple_decode")

    # Verify we can load data of all mapped file types.
    for ext in DataMapping.mapping:
        ext_root = Path(base, str(ext))

        # Verify we can load each file.
        for fname in "abc":
            path = ext.apply(Path(ext_root, fname))
            expected = {f"{fname}_section_1": {"a": "a", "b": "b", "c": "c"}}

            data = ARBITER.decode(path, require_success=True).data
            with suppress(KeyError):
                del data["DEFAULT"]

            assert data == expected
