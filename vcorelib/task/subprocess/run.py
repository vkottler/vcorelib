"""
A task definition for wrapping subprocess's 'run' method.
"""

# built-in
from asyncio.subprocess import PIPE as _PIPE
from asyncio.subprocess import Process as _Process
from sys import executable as _executable

# internal
from vcorelib.asyncio.cli import (
    create_subprocess_shell_log,
    handle_process_cancel,
)
from vcorelib.asyncio.subprocess import create_subprocess_exec_log
from vcorelib.platform import is_windows, reconcile_platform
from vcorelib.task import Inbox as _Inbox
from vcorelib.task import Outbox, Task

__all__ = [
    "is_windows",
    "reconcile_platform",
    "SubprocessLogMixin",
    "SubprocessExec",
    "SubprocessExecStreamed",
    "SubprocessShell",
    "SubprocessShellStreamed",
]


class SubprocessLogMixin(Task):
    """
    A class for creating asyncio subprocesses and logging what gets created.
    """

    async def subprocess_exec(
        self,
        program: str,
        *caller_args,
        args: str = "",
        separator: str = "::",
        stdout: int = None,
        stderr: int = None,
        **kwargs,
    ) -> _Process:
        """
        Create a process using subprocess exec and log what the arguments were.
        """

        return await create_subprocess_exec_log(
            self.log,
            program,
            *[x for x in args.split(separator) + [*caller_args] if x],
            stdout=stdout,
            stderr=stderr,
            **kwargs,
        )

    async def exec(
        self,
        program: str,
        *caller_args,
        args: str = "",
        separator: str = "::",
        stdout: int = None,
        stderr: int = None,
    ) -> bool:
        """Execute a command and return whether or not it succeeded."""

        proc = await handle_process_cancel(
            await self.subprocess_exec(
                program,
                *caller_args,
                args=args,
                separator=separator,
                stdout=stdout,
                stderr=stderr,
            ),
            self.name,
            self.log,
        )
        return proc.returncode == 0

    async def subprocess_shell(
        self,
        cmd: str,
        *caller_args,
        args: str = "",
        joiner: str = " ",
        separator: str = "::",
        stdout: int = None,
        stderr: int = None,
    ) -> _Process:
        """
        Create a process using subprocess shell and log what the command is.
        """

        return await create_subprocess_shell_log(
            self.log,
            cmd
            + joiner.join(
                x for x in args.split(separator) + [*caller_args] if x
            ),
            stdout=stdout,
            stderr=stderr,
        )

    async def shell(
        self,
        cmd: str,
        *caller_args,
        args: str = "",
        joiner: str = " ",
        separator: str = "::",
        stdout: int = None,
        stderr: int = None,
    ) -> bool:
        """Execute a shell command and return whether or not it succeeded."""

        proc = await handle_process_cancel(
            await self.subprocess_shell(
                cmd,
                *caller_args,
                args=args,
                joiner=joiner,
                separator=separator,
                stdout=stdout,
                stderr=stderr,
            ),
            self.name,
            self.log,
        )
        return proc.returncode == 0


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
        require_success: bool = True,
        **kwargs,
    ) -> bool:
        """
        Create a subprocess, wait for it to exit and add results to the outbox.
        """

        proc = await handle_process_cancel(
            await self.subprocess_exec(
                program,
                *caller_args,
                args=args,
                separator=separator,
                stdout=_PIPE,
                stderr=_PIPE,
            ),
            self.name,
            self.log,
        )
        outbox["stdout"] = proc.stdout
        outbox["stderr"] = proc.stderr
        outbox["code"] = proc.returncode

        return True if not require_success else proc.returncode == 0


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
        require_success: bool = True,
        **kwargs,
    ) -> bool:
        """
        Create a subprocess, wait for it to exit and add results to the outbox.
        """

        proc = await handle_process_cancel(
            await self.subprocess_exec(
                program, *caller_args, args=args, separator=separator
            ),
            self.name,
            self.log,
        )
        outbox["code"] = proc.returncode

        return True if not require_success else proc.returncode == 0


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
        require_success: bool = True,
        **kwargs,
    ) -> bool:
        """
        Run a shell command, wait for it to exit and add results to the outbox.
        """

        proc = await handle_process_cancel(
            await self.subprocess_shell(
                cmd,
                *caller_args,
                args=args,
                joiner=joiner,
                separator=separator,
                stdout=_PIPE,
                stderr=_PIPE,
            ),
            self.name,
            self.log,
        )
        outbox["stdout"] = proc.stdout
        outbox["stderr"] = proc.stderr
        outbox["code"] = proc.returncode

        return True if not require_success else proc.returncode == 0


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
        require_success: bool = True,
        **kwargs,
    ) -> bool:
        """
        Run a shell command, wait for it to exit and add results to the outbox.
        """

        proc = await handle_process_cancel(
            await self.subprocess_shell(
                cmd,
                *caller_args,
                args=args,
                joiner=joiner,
                separator=separator,
            ),
            self.name,
            self.log,
        )
        outbox["code"] = proc.returncode

        return True if not require_success else proc.returncode == 0
