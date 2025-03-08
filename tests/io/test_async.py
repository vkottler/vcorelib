"""
Test asyncio integrations in the 'io' module.
"""

# third-party
from pytest import mark

# module under test
from vcorelib.io import ARBITER
from vcorelib.io.types import JsonObject
from vcorelib.paths.context import tempfile


@mark.asyncio
async def test_arbiter_async_basic():
    """Test basic async integrations for DataArbiter."""

    with tempfile(suffix=".json") as tmp:
        data: JsonObject = {"a": 1, "b": 2, "c": 3}
        assert await ARBITER.encode_async(tmp, data)
        result = await ARBITER.decode_async(tmp, require_success=True)
        assert result
        assert result.data == data
