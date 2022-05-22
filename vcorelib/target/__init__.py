"""
A module defining an interface for dynamic task targets.
"""

# built-in
import re
from typing import Dict as _Dict
from typing import List as _List
from typing import NamedTuple as _NamedTuple
from typing import Optional as _Optional
from typing import Tuple as _Tuple

Substitutions = _Dict[str, str]


class DynamicTargetEvaluator(_NamedTuple):
    """
    A regular expression configured to match as many groups as in the provided
    keys. When the pattern matches some data, the names of the keys can become
    associated with the data that was matched inside each group.
    """

    original: str
    pattern: re.Pattern
    keys: _List[str]
    markers: _List[_Tuple[int, int]]

    def compile(self, values: Substitutions) -> str:
        """
        Build a string from this target with values replaced for keys that
        appeared in the original string.
        """

        result = ""
        orig_idx = 0
        for key, marker in zip(self.keys, self.markers):
            result += self.original[orig_idx : marker[0]]
            result += str(values[key])
            orig_idx = marker[1] + 1
        return result


class TargetMatch(_NamedTuple):
    """
    An encapsulation of results when attempting to patch a target name to a
    pattern. If a target was matched and had keyword substitutions, the actual
    values used will be set as match data.
    """

    matched: bool
    substitutions: _Optional[Substitutions] = None

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

    def __str__(self) -> str:
        """Get this target as a string."""
        return self.data

    def __eq__(self, other: object) -> bool:
        """Check if two targets are equal."""
        return str(self) == str(other)

    def __hash__(self) -> int:
        """Get the hash for this target."""
        return hash(str(self))

    @classmethod
    def is_literal(cls, data: str) -> bool:
        """Determine if a target is guaranteed to be literal or not."""
        return (
            data.count(cls.dynamic_start) == data.count(cls.dynamic_end) == 0
        )

    def compile(self, substitutions: Substitutions = None) -> str:
        """
        Attempt to get a target literal from this target and optional
        substitutions.
        """

        result = self.data
        if self.evaluator is not None:
            assert substitutions is not None, f"Can't compile '{self.data}'!"
            result = self.evaluator.compile(substitutions)
        return result

    @classmethod
    def parse(cls, data: str) -> _Optional[DynamicTargetEvaluator]:
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
        markers: _List[_Tuple[int, int]] = []
        live = data
        abs_idx = 0
        for _ in range(open_len):
            start = live.index(cls.dynamic_start)
            end = live.index(cls.dynamic_end)

            # Store the absolute index into the string that the control
            # characters appeared.
            markers.append((abs_idx + start, abs_idx + end))

            pattern += live[:start]
            pattern += f"({cls.valid})"

            keys.append(live[start + 1 : end])
            live = live[end + 1 :]
            abs_idx += end + 1
        pattern += live + "$"

        assert len(keys) == open_len
        return DynamicTargetEvaluator(data, re.compile(pattern), keys, markers)

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
