"""
A module implementing a base channel environment.
"""

# built-in
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Union as _Union
from typing import cast as _cast

# internal
from vcorelib.channel import Channel as _Channel
from vcorelib.channel.registry import ChannelRegistry as _ChannelRegistry
from vcorelib.channel.registry import Channellike as _Channellike
from vcorelib.enum import BoolRuntimeEnum as _BoolRuntimeEnum
from vcorelib.enum import IntRuntimeEnum as _IntRuntimeEnum
from vcorelib.enum import RuntimeEnumType as _RuntimeEnumType
from vcorelib.enum.registry import EnumRegistry as _EnumRegistry
from vcorelib.enum.registry import RegistryKey as _RegistryKey
from vcorelib.math.types.bool import BooleanPrimitive as _BooleanPrimitive
from vcorelib.math.types.float import (
    FloatingPointPrimitive as _FloatingPointPrimitive,
)
from vcorelib.math.types.int import IntegerPrimitive as _IntegerPrimitive
from vcorelib.math.types.primitive import AnyPrimitive as _AnyPrimitive

ValueMap = _Dict[_RegistryKey, _Union[bool, int, float, str]]


class BaseChannelEnvironment:
    """A class integrating channel and enumeration registries."""

    def __init__(
        self,
        channels: _ChannelRegistry = None,
        enums: _EnumRegistry = None,
        values: ValueMap = None,
    ) -> None:
        """Initialize this channel environment."""

        if channels is None:
            channels = _ChannelRegistry()
        if enums is None:
            enums = _EnumRegistry()

        self.channels = channels
        self.enums = enums

        # Keep a mapping of each channel's name and integer identifier to the
        # underlying enumeration.
        self.channel_enums: _Dict[_Channel, _RuntimeEnumType] = {}

        # Wire channels and their enums together.
        for channel in self.channels.channels.values():

            # Ensure that this channel's enumeration exists
            if channel.enum is not None:
                self.channel_enums[channel] = self.enums.get_enum(channel.enum)

        # Create primitives for each channel.
        primitives: _Dict[_Channel, _AnyPrimitive] = {
            chan: chan.type.value() for chan in self.channels.channels.values()
        }

        # Organize channel by language type.
        self.bools: _Dict[_Channel, _BooleanPrimitive] = {
            chan: _cast(_BooleanPrimitive, prim)
            for chan, prim in primitives.items()
            if prim.kind.is_boolean
        }
        self.ints: _Dict[_Channel, _IntegerPrimitive] = {
            chan: _cast(_IntegerPrimitive, prim)
            for chan, prim in primitives.items()
            if prim.kind.is_integer
        }
        self.floats: _Dict[_Channel, _FloatingPointPrimitive] = {
            chan: _cast(_FloatingPointPrimitive, prim)
            for chan, prim in primitives.items()
            if prim.kind.is_float
        }

        # Apply initial values if they were provided.
        if values is not None:
            self.apply(values)

    def apply(self, values: ValueMap) -> None:
        """Apply a map of values to the environment."""

        for key, value in values.items():
            chan = self.channels.get_channel(key)
            assert chan is not None, f"No channel '{key}'!"

            if chan in self.bools:
                self.set_bool(chan, _cast(bool, value))
            elif chan in self.ints:
                self.set_int(chan, _cast(int, value))
            else:
                self.set_float(chan, _cast(float, value))

    def values(self) -> ValueMap:
        """Get a new dictionary of current channel values."""

        # Create a map of channel values. Resolve enum values to strings when
        # applicable.
        data: ValueMap = {}

        # Handle booleans.
        data.update(
            {self.channels.name(x): self.bool_value(x) for x in self.bools}
        )

        # Handle integers.
        data.update(
            {self.channels.name(x): self.int_value(x) for x in self.ints}
        )

        # Handle floats.
        data.update(
            {self.channels.name(x): self.float_value(x) for x in self.floats}
        )

        return data

    def __eq__(self, other) -> bool:
        """Determine if two channel environments are equivalent."""
        return bool(
            self.channels == other.channels and self.enums == other.enums
        )

    def _get_bool(self, val: _Channellike) -> _Optional[_Channel]:
        """Get a boolean channel (and confirm it's boolean)."""
        chan = self.channels.get_channel(val)
        return chan if chan is not None and chan in self.bools else None

    def get_bool(
        self, val: _Channellike
    ) -> _Optional[_Tuple[_BooleanPrimitive, _Optional[_BoolRuntimeEnum]]]:
        """Get a boolean primitive managed by this environment."""

        chan = self._get_bool(val)
        return (
            (
                self.bools[chan],
                _cast(
                    _Optional[_BoolRuntimeEnum], self.channel_enums.get(chan)
                ),
            )
            if chan is not None
            else None
        )

    def bool_value(
        self, val: _Channellike, resolve_enum: bool = True
    ) -> _Union[str, bool]:
        """
        Get a boolean value from a channel and optionally resolve an
        enumeration.
        """

        chan = self.get_bool(val)
        assert chan is not None, f"No boolean channel '{val}'!"

        val = chan[0]()
        if resolve_enum and chan[1] is not None:
            val = chan[1].as_str(val)
        return val

    def set_bool(self, key: _Channellike, value: _Union[str, bool]) -> bool:
        """Set a boolean channel's value."""

        chan = self.get_bool(key)
        if chan is not None:
            if isinstance(value, str):
                assert (
                    chan[1] is not None
                ), f"Can't set a boolean to '{value}'!"
                value = chan[1].as_value(value)
            chan[0](value)
        return chan is not None

    def _get_float(self, val: _Channellike) -> _Optional[_Channel]:
        """Get a boolean channel (and confirm it's boolean)."""
        chan = self.channels.get_channel(val)
        return chan if chan is not None and chan in self.floats else None

    def get_float(
        self, val: _Channellike
    ) -> _Optional[_FloatingPointPrimitive]:
        """Get a boolean primitive managed by this environment."""
        chan = self._get_float(val)
        return self.floats[chan] if chan is not None else None

    def float_value(self, val: _Channellike) -> float:
        """Get the value for a floating-point channel."""

        chan = self.get_float(val)
        assert chan is not None, f"No floating-point channel '{val}'!"
        return chan()

    def set_float(self, key: _Channellike, value: float) -> bool:
        """Set a floating-point channel's value."""

        chan = self.get_float(key)
        if chan is not None:
            chan(value)
        return chan is not None

    def _get_int(self, val: _Channellike) -> _Optional[_Channel]:
        """Get a boolean channel (and confirm it's boolean)."""
        chan = self.channels.get_channel(val)
        return chan if chan is not None and chan in self.ints else None

    def get_int(
        self, val: _Channellike
    ) -> _Optional[_Tuple[_IntegerPrimitive, _Optional[_IntRuntimeEnum]]]:
        """Get a boolean primitive managed by this environment."""

        chan = self._get_int(val)
        return (
            (
                self.ints[chan],
                _cast(
                    _Optional[_IntRuntimeEnum], self.channel_enums.get(chan)
                ),
            )
            if chan is not None
            else None
        )

    def int_value(
        self, val: _Channellike, resolve_enum: bool = True
    ) -> _Union[str, int]:
        """
        Get an integer value from a channel and optionally resolve an
        enumeration.
        """

        chan = self.get_int(val)
        assert chan is not None, f"No integer channel '{val}'!"

        val = chan[0]()
        if resolve_enum and chan[1] is not None:
            val = chan[1].as_str(val)
        return val

    def set_int(self, key: _Channellike, value: _Union[str, int]) -> bool:
        """Set an integer channel's value."""

        chan = self.get_int(key)
        if chan is not None:
            if isinstance(value, str):
                assert (
                    chan[1] is not None
                ), f"Can't set an integer to '{value}'!"
                value = chan[1].as_value(value)
            chan[0](value)
        return chan is not None
