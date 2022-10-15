"""
A module implementing a channel environment.
"""

# internal
from vcorelib.channel.environment.create import (
    CreateChannelEnvironment as _CreateChannelEnvironment,
)
from vcorelib.channel.environment.file import (
    FileChannelEnvironment as _FileChannelEnvironment,
)


class ChannelEnvironment(_FileChannelEnvironment, _CreateChannelEnvironment):
    """A class integrating channel and enumeration registries."""
