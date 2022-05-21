"""
A task definition for wrapping subprocess's 'run' method.
"""

# built-in
from asyncio import create_subprocess_exec, create_subprocess_shell
from asyncio.subprocess import PIPE as _PIPE
from sys import executable as _executable

# internal
from vcorelib.task import Inbox as _Inbox
from vcorelib.task import Outbox, Task


class SubprocessExec(Task):
    """A task wrapping a subprocess."""

    async def run(
        self,
        inbox: _Inbox,
        outbox: Outbox,
        *caller_args,
        args: str = "--version",
        program: str = _executable,
        separator: str = "::",
        **kwargs,
    ) -> bool:
        """
        Create a subprocess, wait for it to exit and add results to the outbox.
        """

        proc = await create_subprocess_exec(
            program,
            *(args.split(separator) + list(*caller_args)),
            stdout=_PIPE,
            stderr=_PIPE,
        )
        stdout, stderr = await proc.communicate()
        outbox["stdout"] = stdout
        outbox["stderr"] = stderr
        outbox["code"] = proc.returncode

        return True


class SubprocessExecStreamed(Task):
    """A task wrapping a subprocess."""

    async def run(
        self,
        inbox: _Inbox,
        outbox: Outbox,
        *caller_args,
        args: str = "--version",
        program: str = _executable,
        separator: str = "::",
        **kwargs,
    ) -> bool:
        """
        Create a subprocess, wait for it to exit and add results to the outbox.
        """

        proc = await create_subprocess_exec(
            program,
            *(args.split(separator) + list(*caller_args)),
        )
        await proc.communicate()
        outbox["code"] = proc.returncode

        return True


class SubprocessShell(Task):
    """A task wrapping a shell command."""

    async def run(
        self,
        inbox: _Inbox,
        outbox: Outbox,
        *caller_args,
        args: str = "",
        cmd: str = f"{_executable} --version",
        joiner: str = " ",
        separator: str = "::",
        **kwargs,
    ) -> bool:
        """
        Run a shell command, wait for it to exit and add results to the outbox.
        """

        proc = await create_subprocess_shell(
            cmd + joiner.join(args.split(separator) + list(*caller_args)),
            stdout=_PIPE,
            stderr=_PIPE,
        )
        stdout, stderr = await proc.communicate()
        outbox["stdout"] = stdout
        outbox["stderr"] = stderr
        outbox["code"] = proc.returncode

        return True


class SubprocessShellStreamed(Task):
    """A task wrapping a shell command."""

    async def run(
        self,
        inbox: _Inbox,
        outbox: Outbox,
        *caller_args,
        args: str = "",
        cmd: str = f"{_executable} --version",
        joiner: str = " ",
        separator: str = "::",
        **kwargs,
    ) -> bool:
        """
        Run a shell command, wait for it to exit and add results to the outbox.
        """

        proc = await create_subprocess_shell(
            cmd + joiner.join(args.split(separator) + list(*caller_args)),
        )
        await proc.communicate()
        outbox["code"] = proc.returncode

        return True
