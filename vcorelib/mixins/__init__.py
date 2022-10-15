"""
A module for generic class mixins.
"""

# built-in
from re import Pattern as _Pattern


class RegexMixin:  # pylint: disable=too-few-public-methods
    """A simple class mixin for validating names."""

    name_regex: _Pattern  # type: ignore

    @classmethod
    def validate_name(cls, name: str, strict: bool = True) -> bool:
        """Verify that a key name is valid."""

        result = bool(cls.name_regex.fullmatch(name))
        if strict:
            assert result, f"Invalid name '{name}'!"
        return result
