"""
A channel-environment extension for loading and saving files.
"""

# built-in
from typing import Optional as _Optional
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import cast as _cast

# internal
from vcorelib.channel.environment.base import (
    BaseChannelEnvironment as _BaseChannelEnvironment,
)
from vcorelib.channel.environment.base import ValueMap as _ValueMap
from vcorelib.channel.registry import ChannelRegistry as _ChannelRegistry
from vcorelib.enum.registry import EnumRegistry as _EnumRegistry
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize as _normalize

T = _TypeVar("T", bound="FileChannelEnvironment")
CHANNELS_FILE = "channels.json"
ENUMS_FILE = "enums.json"
VALUES_FILE = "values.json"


class FileChannelEnvironment(_BaseChannelEnvironment):
    """A class integrating file-system operations with channel environments."""

    def export(
        self,
        channels: _Pathlike = CHANNELS_FILE,
        enums: _Pathlike = ENUMS_FILE,
        values: _Pathlike = VALUES_FILE,
        **kwargs,
    ) -> None:
        """Write channel and enum registries to disk."""

        self.channels.encode(channels, **kwargs)
        self.enums.encode(enums, **kwargs)
        _ARBITER.encode(values, _cast(_JsonObject, self.values()), **kwargs)

    def export_directory(self, path: _Pathlike) -> None:
        """Export this channel environment to a directory."""

        path = _normalize(path)
        path.mkdir(parents=True, exist_ok=True)
        self.export(
            channels=path.joinpath(CHANNELS_FILE),
            enums=path.joinpath(ENUMS_FILE),
            values=path.joinpath(VALUES_FILE),
        )

    @classmethod
    def load(
        cls: _Type[T],
        channels: _Pathlike = CHANNELS_FILE,
        enums: _Pathlike = ENUMS_FILE,
        values: _Pathlike = VALUES_FILE,
    ) -> T:
        """Load a channel environment from a pair of files."""

        value_map: _Optional[_ValueMap] = None

        # Load the value map if it's present.
        values = _normalize(values)
        if values.is_file():
            value_map = _cast(
                _ValueMap, _ARBITER.decode(values, require_success=True).data
            )

        return cls(
            channels=_ChannelRegistry.decode(channels),
            enums=_EnumRegistry.decode(enums),
            values=value_map,
        )

    @classmethod
    def load_directory(cls: _Type[T], path: _Pathlike) -> T:
        """Load a channel environment from a directory."""

        path = _normalize(path, require=True)
        assert path.is_dir(), f"'{path}' is not a directory!"
        return cls.load(
            channels=path.joinpath(CHANNELS_FILE),
            enums=path.joinpath(ENUMS_FILE),
            values=path.joinpath(VALUES_FILE),
        )
