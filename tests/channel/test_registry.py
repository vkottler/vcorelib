"""
Test the 'channel.registry' module.
"""

# internal
from tests.resources import resource

# module under test
from vcorelib.channel.registry import ChannelRegistry
from vcorelib.math.types.enum import PrimitiveTypes


def test_channel_registry_simple():
    """Test interactions with a channel registry."""

    registry = ChannelRegistry.decode(
        resource("channels", "sample_registry.yaml")
    )
    for i in range(10):
        registry.register(f"new_channel{i}", "bool")
        registry.register(f"new_channel{i}0", PrimitiveTypes.FLOAT)

    assert registry.by_id[1] == registry.by_id[1]
