"""
Test the 'asyncio.cli' module.
"""

# built-in
from logging import getLogger
from sys import executable

# third-party
from pytest import mark

# module under test
from vcorelib.asyncio.cli import run_command, run_shell


@mark.asyncio
async def test_asyncio_cli_basic():
    """Test basic interactions with CLI interfaces."""

    log = getLogger(__name__)

    assert (
        await run_command(log, executable, "--version")
    ).returncode is not None
    assert (
        await run_shell(log, executable, "--version")
    ).returncode is not None
