"""
A task definition for wrapping subprocess's 'run' method.
"""

# built-in
import asyncio
from sys import executable

# internal
from vcorelib.task import Inbox, Outbox, Task


class SubprocessExec(Task):
    """A task wrapping a subprocess."""

    async def run(
        self,
        inbox: Inbox,
        outbox: Outbox,
        *caller_args,
        args: str = "--version",
        program: str = executable,
        separator: str = "::",
        **kwargs,
    ) -> bool:
        """
        Create a subprocess, wait for it to exit and add results to the outbox.
        """

        proc = await asyncio.create_subprocess_exec(
            program,
            *(args.split(separator) + list(*caller_args)),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        outbox["stdout"] = stdout
        outbox["stderr"] = stderr
        outbox["code"] = proc.returncode

        return True


class SubprocessShell(Task):
    """A task wrapping a shell command."""

    async def run(
        self,
        inbox: Inbox,
        outbox: Outbox,
        *caller_args,
        args: str = "",
        cmd: str = f"{executable} --version",
        joiner: str = " ",
        separator: str = "::",
        **kwargs,
    ) -> bool:
        """
        Run a shell command, wait for it to exit and add results to the outbox.
        """

        proc = await asyncio.create_subprocess_shell(
            cmd + joiner.join(args.split(separator) + list(*caller_args)),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        outbox["stdout"] = stdout
        outbox["stderr"] = stderr
        outbox["code"] = proc.returncode

        return True
