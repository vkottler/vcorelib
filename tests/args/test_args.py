"""
Test the 'args' module.
"""

# built-in
from argparse import ArgumentParser, Namespace

# module under test
from vcorelib.args import CommandFunction, app_args


def test_app_args_basic():
    """Test basic functions of the sub-command builder."""

    def command_function(args: Namespace) -> int:
        """A sample command."""
        del args
        return 0

    def command_register(parser: ArgumentParser) -> CommandFunction:
        """Register the above command."""
        del parser
        return command_function

    cmds = [("a", "sample command", command_register)]
    parser = ArgumentParser()

    arg_adder, command = app_args(lambda: cmds)
    arg_adder(parser)

    parsed = parser.parse_args(["a"])
    assert command(parsed) == 0
