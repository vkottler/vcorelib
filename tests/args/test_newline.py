"""
Tests for the 'args.newline' module.
"""

from argparse import ArgumentParser

# built-in
from os import linesep

# module under test
from vcorelib.args.newline import add_newline_arg


def test_args_newline_basic():
    """Test that we can parse the line-ending argument option."""

    parser = ArgumentParser()
    add_newline_arg(parser)

    args = parser.parse_args([])
    assert args.line_ending == "\n"

    args = parser.parse_args(["--line-ending", "unix"])
    assert args.line_ending == "\n"

    args = parser.parse_args(["--line-ending", "dos"])
    assert args.line_ending == "\r\n"

    args = parser.parse_args(["--line-ending", "platform"])
    assert args.line_ending == linesep
