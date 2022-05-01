"""
Test the 'DataArbiter' class.
"""

# built-in
from contextlib import suppress
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

# internal
from tests.resources import resource

# module under test
from vcorelib.io import ARBITER, DataMapping
from vcorelib.io.definitions import FileExtension


def test_arbiter_encode_decode_basic():
    """Verify that we can load data of every file type."""

    base = resource("simple_decode")

    # Verify we can load data of all mapped file types.
    for ext in DataMapping.mapping:
        ext_root = Path(base, str(ext))

        # Verify that we can decode the entire directory at once.
        data = ARBITER.decode_directory(ext_root, require_success=True).data
        assert data

        # Verify we can encode an entire directory at once.
        with TemporaryDirectory() as tmpdir:
            assert ARBITER.encode_directory(tmpdir, data, ext=str(ext))[0]
            assert not ARBITER.encode_directory(tmpdir, data, ext="unknown")[0]

        # Verify we can load each file.
        for fname in "abc":
            path = ext.apply(Path(ext_root, fname))
            expected = {f"{fname}_section_1": {"a": "a", "b": "b", "c": "c"}}

            data = ARBITER.decode(
                path, require_success=True, preprocessor=lambda x: x
            ).data
            with suppress(KeyError):
                del data["DEFAULT"]

            assert data == expected

            # Verify we can encode data.
            with NamedTemporaryFile(suffix=f".{str(ext)}") as tfile:
                ARBITER.encode(tfile.name, data)


def test_arbiter_decode_empty():
    """Verify we can decode certain kinds of empty files."""

    empty = resource("simple_decode").joinpath("empty")
    counter = 0

    for ext in DataMapping.mapping:
        candidate = ext.apply(empty.joinpath("empty"))
        if candidate.is_file():
            data = ARBITER.decode(candidate).data
            assert not data
            counter += 1

    assert counter == 2


def test_arbiter_decode_failures():
    """Test various invalid loading scenarios."""

    base = resource("simple_decode", False)

    # Verify we can't load data of all mapped file types.
    for ext in list(DataMapping.mapping.keys()) + [FileExtension.UNKNOWN]:
        ext_root = Path(base, str(ext))
        for fname in "abc":
            path = ext.apply(Path(ext_root, fname))
            assert not ARBITER.decode(path).success

            if ext is FileExtension.UNKNOWN:
                with path.open(encoding="utf-8") as path_fd:
                    assert not ARBITER.decode_stream(str(ext), path_fd).success


def test_arbiter_decode_directory_recurse():
    """Ensure we can successfully recurse a directory."""

    assert ARBITER.decode_directory(
        resource("simple_decode").joinpath("recurse"),
        require_success=True,
        recurse=True,
    ).data == {
        "a_section_1": {"a": "a", "b": "b", "c": "c"},
        "b_section_1": {"a": "a", "b": "b", "c": "c"},
        "c_section_1": {"a": "a", "b": "b", "c": "c"},
    }


def test_arbiter_decode_includes():
    """Test that we can load data via the 'includes' key."""

    assert ARBITER.decode_directory(
        resource("simple_decode").joinpath("includes"),
        require_success=True,
        includes_key="includes",
    ).data == {
        "a_section_1": {"a": "a", "b": "b", "c": "c"},
        "b_section_1": {"a": "a", "b": "b", "c": "c"},
        "c_section_1": {"a": "a", "b": "b", "c": "c"},
    }
