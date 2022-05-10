"""
Implements management of target objects.
"""

# built-in
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
)

# internal
from vcorelib.target import LITERAL_MATCH, NO_MATCH, Target, TargetMatch


class TargetResolution(NamedTuple):
    """A return type for the target resolver."""

    result: TargetMatch
    data: Optional[Any] = None


NOT_RESOLVED = TargetResolution(NO_MATCH, None)


class TargetResolver:
    """
    A class for registering target prototypes that can be used to match
    incoming data.
    """

    def __init__(self) -> None:
        """Initialize this target resolver."""

        self.literals: Dict[str, Any] = {}
        self.dynamic: Dict[Target, Any] = {}

    def register(self, data: str, value: Any = None) -> None:
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
            return TargetResolution(LITERAL_MATCH, self.literals[data])

        matches: List[Tuple[Target, TargetMatch, Any]] = []
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
        self, data: Iterable[str], ensure_match: bool = True
    ) -> Iterator[TargetResolution]:
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
