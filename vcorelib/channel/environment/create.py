"""
An environment extension for creating channels and enumerations.
"""

# internal
from vcorelib.channel.environment.base import (
    BaseChannelEnvironment as _BaseChannelEnvironment,
)


class CreateChannelEnvironment(_BaseChannelEnvironment):
    """A class integrating file-system operations with channel environments."""
