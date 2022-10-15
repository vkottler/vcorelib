"""
Test the 'channel.environment' module.
"""

# built-in
from tempfile import TemporaryDirectory

# internal
from tests.resources import resource

# module under test
from vcorelib.channel.environment import ChannelEnvironment


def test_channel_environment_basic():
    """Test basic interactions with a channel environment."""

    env = ChannelEnvironment()
    env = ChannelEnvironment.load_directory(
        resource("channels", "environment", "sample")
    )
    assert env

    assert env.channels.name(1) == "bool.1"

    # Verify values.
    assert env.bool_value("bool.1") is True
    assert env.bool_value("bool.2") == "on"
    assert env.bool_value("bool.3") == "off"
    assert env.int_value("int.1") == 5
    assert env.int_value("int.2", resolve_enum=False) == 4
    assert env.int_value("int.3") == "error"
    assert env.float_value("float.1") == 0.0
    assert env.float_value("float.2") == 1.0

    chan = env.channels.get_channel("int.2")
    assert chan is not None and chan.is_enum

    # Verify exporting and re-importing the environment.
    with TemporaryDirectory() as tmpdir:
        env.export_directory(tmpdir)
        assert env == ChannelEnvironment.load_directory(tmpdir)

    assert env.get_bool("bool.1") is not None
    assert env.get_bool(1) is not None

    assert env.get_float("float.1") is not None
    assert env.get_float(7) is not None

    assert env.get_int("int.1") is not None
    assert env.get_int(4) is not None
