"""
Implements management of target objects.
"""

# built-in
from typing import List, Set, Tuple

# internal
from vcorelib.target import LITERAL_MATCH, NO_MATCH, Target, TargetMatch


class TargetResolver:
    """
    A class for registering target prototypes that can be used to match
    incoming data.
    """

    def __init__(self) -> None:
        """Initialize this target resolver."""

        self.literals: Set[str] = set()
        self.dynamic: List[Target] = []

    def register(self, data: str) -> None:
        """Register a target to this resolver."""

        target = Target(data)
        if target.literal:
            self.literals.add(data)
            return
        self.dynamic.append(target)

    def evaluate(self, data: str) -> TargetMatch:
        """Find the target that matches data, if one can be found."""

        # Optimize matching candidate data against many targets by first
        # testing the literal set.
        if data in self.literals:
            return LITERAL_MATCH

        matches: List[Tuple[Target, TargetMatch]] = []
        for candidate in self.dynamic:
            test = candidate.evaluate(data)
            if test.matched:
                matches.append((candidate, test))

        # If we find any dynamic match, ensure that we only matched a single
        # target.
        if matches:
            assert len(matches) == 1, (
                f"Matched '{data}' to {len(matches)} targets: "
                f"{', '.join(x[0].data for x in matches)}!"
            )
            return matches[0][1]

        return NO_MATCH
