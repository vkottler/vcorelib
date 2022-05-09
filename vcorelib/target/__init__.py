"""
A module defining an interface for dynamic task targets.
"""

# built-in
import re
from typing import Dict, List, NamedTuple, Optional


class DynamicTargetEvaluator(NamedTuple):
    """
    A regular expression configured to match as many groups as in the provided
    keys. When the pattern matches some data, the names of the keys can become
    associated with the data that was matched inside each group.
    """

    pattern: re.Pattern
    keys: List[str]


class TargetMatch(NamedTuple):
    """
    An encapsulation of results when attempting to patch a target name to a
    pattern. If a target was matched and had keyword substitutions, the actual
    values used will be set as match data.
    """

    matched: bool
    substitutions: Optional[Dict[str, str]] = None

    def get(self, data: str) -> str:
        """Get data for keys that matched the target."""
        subs = self.substitutions if self.substitutions is not None else {}
        return subs[data]


LITERAL_MATCH = TargetMatch(True)
NO_MATCH = TargetMatch(False)


class Target:
    """
    An interface for string targets that may encode data substitutions or
    otherwise be matched to only a single, literal string.
    """

    dynamic_start = "{"
    dynamic_end = "}"
    valid = "[a-zA-Z0-9-_.]+"

    def __init__(self, data: str) -> None:
        """Initialize this target."""

        self.data = data
        self.evaluator = self.parse(self.data)
        self.literal = self.evaluator is None

    @classmethod
    def is_literal(cls, data: str) -> bool:
        """Determine if a target is guaranteed to be literal or not."""
        return (
            data.count(cls.dynamic_start) == data.count(cls.dynamic_end) == 0
        )

    @classmethod
    def parse(cls, data: str) -> Optional[DynamicTargetEvaluator]:
        """
        Obtain a compiled target evaluator if data is a dynamic target, else
        None.
        """

        # The short-circuit case where this is not a dynamic target.
        if cls.is_literal(data):
            return None

        # A preliminary syntax check.
        open_len = data.count(cls.dynamic_start)
        assert open_len == data.count(cls.dynamic_end)

        pattern = "^"
        keys = []
        for _ in range(open_len):
            start = data.index(cls.dynamic_start) + 1
            end = data.index(cls.dynamic_end)
            pattern += data[: start - 1]
            pattern += f"({cls.valid})"
            keys.append(data[start:end])
            data = data[end + 1 :]
        pattern += data + "$"

        assert len(keys) == open_len
        return DynamicTargetEvaluator(re.compile(pattern), keys)

    def evaluate(self, data: str) -> TargetMatch:
        """Attempt to match this target with some string data."""

        if self.literal:
            return TargetMatch(self.data == data)

        assert self.evaluator is not None
        result = self.evaluator.pattern.fullmatch(data)
        if result is None:
            return NO_MATCH

        return TargetMatch(
            True,
            {
                key: result.group(1 + idx)
                for idx, key in enumerate(self.evaluator.keys)
            },
        )
