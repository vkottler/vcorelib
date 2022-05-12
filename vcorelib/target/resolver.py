"""
Implements management of target objects.
"""

# built-in
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Iterable as _Iterable
from typing import Iterator as _Iterator
from typing import List as _List
from typing import NamedTuple as _NamedTuple
from typing import Optional as _Optional
from typing import Tuple as _Tuple

# internal
from vcorelib.target import LITERAL_MATCH as _LITERAL_MATCH
from vcorelib.target import NO_MATCH as _NO_MATCH
from vcorelib.target import Target, TargetMatch


class TargetResolution(_NamedTuple):
    """A return type for the target resolver."""

    result: TargetMatch
    data: _Optional[_Any] = None


NOT_RESOLVED = TargetResolution(_NO_MATCH, None)


class TargetResolver:
    """
    A class for registering target prototypes that can be used to match
    incoming data.
    """

    def __init__(self) -> None:
        """Initialize this target resolver."""

        self.literals: _Dict[str, _Any] = {}
        self.dynamic: _Dict[Target, _Any] = {}

    def register(self, data: str, value: _Any = None) -> None:
        """
        Register a target to this resolver. If it is ever resolved in
        evaluation, value will be returned.
        """

        target = Target(data)
        if target.literal:
            self.literals[data] = value
            return
        self.dynamic[target] = value

    def evaluate(self, data: str) -> TargetResolution:
        """Find the target that matches data, if one can be found."""

        # Optimize matching candidate data against many targets by first
        # testing the literal set.
        if data in self.literals:
            return TargetResolution(_LITERAL_MATCH, self.literals[data])

        matches: _List[_Tuple[Target, TargetMatch, _Any]] = []
        for candidate, value in self.dynamic.items():
            test = candidate.evaluate(data)
            if test.matched:
                matches.append((candidate, test, value))

        # If we find any dynamic match, ensure that we only matched a single
        # target.
        if matches:
            assert len(matches) == 1, (
                f"Matched '{data}' to {len(matches)} targets: "
                f"{', '.join(x[0].data for x in matches)}!"
            )
            return TargetResolution(matches[0][1], matches[0][2])

        return NOT_RESOLVED

    def evaluate_all(
        self, data: _Iterable[str], ensure_match: bool = True
    ) -> _Iterator[TargetResolution]:
        """
        Evaluate all targets and optionally enforce that they all matched.
        """

        for item in data:
            evaluation = self.evaluate(item)

            # Optionally enforce that all targets are resolved.
            if ensure_match:
                assert (
                    evaluation.result.matched
                ), f"Couldn't match '{item}' to any target!"

            yield evaluation
