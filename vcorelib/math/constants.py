"""
A module defining some useful constants.
"""

MILLION = 1_000_000
BILLION = MILLION * 1_000


def from_nanos(nanos: int) -> float:
    """Convert a number in nano counts to a regular floating-point number."""
    return nanos / BILLION


def to_nanos(value: float) -> int:
    """Convert a number to the same number but in nano counts."""
    return int(value * BILLION)
