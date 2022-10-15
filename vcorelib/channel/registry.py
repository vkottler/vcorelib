"""
A module implementing a channel registry.
"""

# built-in
from re import compile as _compile
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Union as _Union
from typing import cast as _cast

# internal
from vcorelib.channel import Channel as _Channel
from vcorelib.dict.codec import DictCodec as _DictCodec
from vcorelib.enum.registry import RegistryKey as _RegistryKey
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.math.types.enum import PrimitiveTypelike as _PrimitiveTypelike
from vcorelib.math.types.enum import normalize_type as _normalize_type
from vcorelib.mixins import RegexMixin as _RegexMixin
from vcorelib.schemas import json_schemas as _json_schemas
from vcorelib.schemas.base import SchemaMap as _SchemaMap

Channellike = _Union[_RegistryKey, _Channel]


class ChannelRegistry(_DictCodec, _RegexMixin):
    """A simple channel registry."""

    default_schemas: _Optional[_SchemaMap] = _json_schemas()

    # Note that this needs to be kept synchronized with the JSON schema.
    name_regex = _compile("^[a-z0-9_.]+$")

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        self.current = 1
        self.channels: _Dict[str, _Channel] = {}
        self.by_id: _Dict[int, _Channel] = {}
        self.names: _Dict[_Channel, str] = {}

        # Initialize channels.
        for name, chan_data in data.items():
            self.validate_name(name)
            channel = _Channel.from_dict(_cast(_JsonObject, chan_data))
            self.channels[name] = channel
            self.by_id[channel.id] = channel
            self.names[channel] = name

        # Update the current identifier value.
        for identifier in self.by_id:
            if identifier >= self.current:
                self.current = identifier + 1

    def _register_name(self, name: str) -> _Optional[int]:
        """Register a new channel name."""

        result = self.validate_name(name, strict=False)
        result &= name not in self.channels

        identifier = None
        if result:
            while self.current in self.by_id:
                self.current += 1
            identifier = self.current

        return identifier

    def get_channel(self, val: Channellike) -> _Optional[_Channel]:
        """Attempt to look up a channel from its name or identifier."""

        if isinstance(val, int):
            return self.by_id.get(val)
        if isinstance(val, str):
            return self.channels.get(val)
        return val

    def normalize(self, val: Channellike) -> _Channel:
        """Convert any input argument into a channel."""

        if not isinstance(val, _Channel):
            chan = self.get_channel(val)
            assert chan is not None, f"No channel '{val}'!"
            val = chan

        return val

    def name(self, val: Channellike) -> str:
        """Obtain a channel name."""
        return self.names[self.normalize(val)]

    def register(
        self,
        name: str,
        kind: _PrimitiveTypelike,
        commandable: bool = False,
        enum: _Optional[_RegistryKey] = None,
    ) -> _Channel:
        """Register a new channel."""

        identifier = self._register_name(name)
        assert identifier is not None, f"Invalid channel name '{name}'!"

        result = _Channel(identifier, _normalize_type(kind), commandable, enum)
        self.channels[name] = result
        self.by_id[result.id] = result
        self.names[result] = name
        return result

    def asdict(self) -> _JsonObject:
        """Obtain a dictionary representing this instance."""

        return {
            name: channel.asdict() for name, channel in self.channels.items()
        }
