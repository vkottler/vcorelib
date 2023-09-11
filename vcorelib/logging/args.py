"""
A module implementing command-line option handling for logger initialization.
"""

# built-in
import argparse
import logging
from typing import Iterable, Iterator

DEFAULT_FORMAT = "%(name)-36s - %(levelname)-6s - %(message)s"


def init_logging(
    args: argparse.Namespace, default_format: str = DEFAULT_FORMAT
) -> None:
    """Initialize logging based on command-line arguments."""

    if not (getattr(args, "quiet", False) or getattr(args, "curses", False)):
        logging.basicConfig(
            level=logging.DEBUG if args.verbose else logging.INFO,
            format=default_format,
        )


def logging_args(parser: argparse.ArgumentParser) -> None:
    """Add logging related command-line arguments to a parser."""

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="set to increase logging verbosity",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="set to reduce output"
    )
    parser.add_argument(
        "--curses",
        action="store_true",
        help="whether or not to use curses.wrapper when starting",
    )


def forward_flags(
    args: argparse.Namespace, names: Iterable[str]
) -> Iterator[str]:
    """Forward flag arguments."""

    for name in names:
        if getattr(args, name, False):
            yield f"--{name}"


def forward_logging_flags(args: argparse.Namespace) -> Iterator[str]:
    """
    Forward logging-related flags passed to this program to some other
    program.
    """
    yield from forward_flags(args, ["verbose", "quiet", "curses"])
