"""
A task definition for wrapping subprocess's 'run' method.
"""

# built-in
from asyncio import create_subprocess_exec, create_subprocess_shell
from asyncio.subprocess import PIPE as _PIPE
from asyncio.subprocess import Process as _Process
from sys import executable as _executable

# internal
from vcorelib.task import Inbox as _Inbox
from vcorelib.task import Outbox, Task


class SubprocessLogMixin(Task):
    """
    A class for creating asyncio subprocesses and logging what gets created.
    """

    async def subprocess_exec(
        self,
        program: str,
        args: str,
        separator: str,
        *caller_args,
        stdout: int = None,
        stderr: int = None,
    ) -> _Process:
        """
        Create a process using subprocess exec and log what the arguments were.
        """

        exec_args = args.split(separator) + list(*caller_args)
        self.log.info("exec '%s': %s", program, " ".join(exec_args))
        proc = await create_subprocess_exec(
            program,
            *exec_args,
            stdout=stdout,
            stderr=stderr,
        )
        return proc

    async def subprocess_shell(
        self,
        cmd: str,
        args: str,
        joiner: str,
        separator: str,
        *caller_args,
        stdout: int = None,
        stderr: int = None,
    ) -> _Process:
        """
        Create a process using subprocess shell and log what the command is.
        """

        command = cmd + joiner.join(args.split(separator) + list(*caller_args))
        self.log.info("shell: '%s'", command)
        proc = await create_subprocess_shell(
            command, stdout=stdout, stderr=stderr
        )
        return proc


class SubprocessExec(SubprocessLogMixin):
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

        proc = await self.subprocess_exec(
            program,
            args,
            separator,
            *caller_args,
            stdout=_PIPE,
            stderr=_PIPE,
        )
        stdout, stderr = await proc.communicate()
        outbox["stdout"] = stdout
        outbox["stderr"] = stderr
        outbox["code"] = proc.returncode

        return True


class SubprocessExecStreamed(SubprocessLogMixin):
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

        proc = await self.subprocess_exec(
            program, args, separator, *caller_args
        )
        await proc.communicate()
        outbox["code"] = proc.returncode

        return True


class SubprocessShell(SubprocessLogMixin):
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

        proc = await self.subprocess_shell(
            cmd,
            args,
            joiner,
            separator,
            *caller_args,
            stdout=_PIPE,
            stderr=_PIPE,
        )
        stdout, stderr = await proc.communicate()
        outbox["stdout"] = stdout
        outbox["stderr"] = stderr
        outbox["code"] = proc.returncode

        return True


class SubprocessShellStreamed(SubprocessLogMixin):
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

        proc = await self.subprocess_shell(
            cmd, args, joiner, separator, *caller_args
        )
        await proc.communicate()
        outbox["code"] = proc.returncode

        return True
