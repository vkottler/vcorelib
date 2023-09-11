"""
Test the 'logging.args' module.
"""

# built-in
from argparse import ArgumentParser

# module under test
from vcorelib.logging import forward_logging_flags, init_logging, logging_args


def test_logging_args_basic():
    """Test basic command-line option parsing for logging."""

    parser = ArgumentParser()

    logging_args(parser)

    args = parser.parse_args([])
    init_logging(args)

    assert list(forward_logging_flags(parser.parse_args(["-q"]))) == [
        "--quiet"
    ]
