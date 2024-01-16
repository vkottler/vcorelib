"""
Test the 'dict.codec' module.
"""

# built-in
from copy import copy
from pathlib import Path
from tempfile import NamedTemporaryFile

# third-party
from pytest import raises

# internal
from tests.resources import get_test_schemas, resource

# module under test
from vcorelib.dict import codec
from vcorelib.paths.context import tempfile
from vcorelib.schemas.base import SchemaValidationError


def test_dict_codec_file_cache():
    """Test the 'file_cache' method."""

    with tempfile(suffix=".yaml") as path:
        with codec.BasicDictCodec.file_cache(path) as inst:
            inst.data["a"] = 1
            inst.data["b"] = 2
            inst.data["c"] = 3

        # Load and confirm.
        inst = codec.BasicDictCodec.decode(path)
        assert inst.data["a"] == 1
        assert inst.data["b"] == 2
        assert inst.data["c"] == 3


def test_dict_codec_basic():
    """Test basic interactions and instantiations of dict-codec objects."""

    # Load valid data.
    valid = codec.BasicDictCodec.decode(
        resource("test.json"), schemas=get_test_schemas()
    )
    assert valid.asdict()["a"] == 42

    assert str(valid)

    assert valid == codec.BasicDictCodec.decode(
        resource("test.json"), schemas=get_test_schemas()
    )

    # Write the object to a temporary file.
    with NamedTemporaryFile(suffix=".json", delete=False) as temp:
        name = temp.name
    valid.encode(name)
    Path(name).unlink()

    assert codec.BasicDictCodec()

    # Test copying.
    copied = copy(valid)
    assert copied == valid
    copied.data["c"] = False
    assert copied != valid


def test_dict_codec_error():
    """Confirm that data violating a schema raises an exception."""

    # Load invalid data that violates the schema.
    with raises(SchemaValidationError):
        codec.BasicDictCodec.decode(
            resource("test.json", valid=False),
            schemas=get_test_schemas(),
        )

    inst = codec.BasicDictCodec.normalize({"a": 1})
    assert inst == {"a": 1}
    assert codec.BasicDictCodec.normalize(inst) == {"a": 1}
