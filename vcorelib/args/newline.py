"""
A module for adding newline-related arguments to an argument parser.
"""

# built-in
from argparse import ArgumentParser
from enum import Enum
from os import linesep


class LineEnding(str, Enum):
    """An enumeration for line-ending options."""

    UNIX = "\n"
    DOS = "\r\n"
    PLATFORM = linesep

    def __str__(self) -> str:
        """Get this enum as a string."""
        result = "platform"
        if self is LineEnding.UNIX:
            result = "unix"
        if self is LineEnding.DOS:
            result = "dos"
        return result

    @staticmethod
    def from_arg(opt: str) -> "LineEnding":
        """Convert a string option to an instance of this enum."""
        opt = opt.lower()
        if opt == "unix":
            return LineEnding.UNIX
        if opt == "dos":
            return LineEnding.DOS
        return LineEnding.PLATFORM


def add_newline_arg(parser: ArgumentParser) -> None:
    """Add a line-ending argument to an argument parser."""

    choices = [LineEnding.UNIX, LineEnding.DOS, LineEnding.PLATFORM]
    parser.add_argument(
        "--line-ending",
        type=LineEnding.from_arg,
        default="unix",
        choices=choices,
        help="line-ending option to use by default (default: '%(default)s')",
    )
