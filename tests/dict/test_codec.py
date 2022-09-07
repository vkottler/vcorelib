"""
Test the 'dict.codec' module.
"""

# built-in
from pathlib import Path
from tempfile import NamedTemporaryFile

# third-party
from pytest import raises

# internal
from tests.resources import resource, test_schemas

# module under test
from vcorelib.dict import codec
from vcorelib.schemas import SchemaValidationError


def test_dict_codec_basic():
    """Test basic interactions and instantiations of dict-codec objects."""

    # Load valid data.
    valid = codec.ValidatedDictCodec.decode(
        codec.BasicDictCodec, resource("test.json"), test_schemas()
    )
    assert valid.to_dict()["a"] == 42

    # Write the object to a temporary file.
    with NamedTemporaryFile(suffix=".json", delete=False) as temp:
        name = temp.name
    valid.encode(name)
    Path(name).unlink()

    # Load invalid data that violates the schema.
    with raises(SchemaValidationError):
        codec.ValidatedDictCodec.decode(
            codec.BasicDictCodec,
            resource("test.json", valid=False),
            test_schemas(),
        )
