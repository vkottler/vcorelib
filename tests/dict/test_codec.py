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
    valid = codec.BasicDictCodec.decode(
        resource("test.json"), schemas=test_schemas()
    )
    assert valid.asdict()["a"] == 42

    assert str(valid)

    assert valid == codec.BasicDictCodec.decode(
        resource("test.json"), schemas=test_schemas()
    )

    # Write the object to a temporary file.
    with NamedTemporaryFile(suffix=".json", delete=False) as temp:
        name = temp.name
    valid.encode(name)
    Path(name).unlink()

    # Load invalid data that violates the schema.
    with raises(SchemaValidationError):
        codec.BasicDictCodec.decode(
            resource("test.json", valid=False),
            schemas=test_schemas(),
        )
