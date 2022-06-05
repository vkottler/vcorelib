"""
A task definition for wrapping subprocess's 'run' method.
"""

# built-in
from asyncio import create_subprocess_exec, create_subprocess_shell
from asyncio.subprocess import PIPE as _PIPE
from asyncio.subprocess import Process as _Process
from platform import system as _system
from sys import executable as _executable
from typing import List as _List
from typing import Tuple as _Tuple

# internal
from vcorelib.task import Inbox as _Inbox
from vcorelib.task import Outbox, Task


def is_windows() -> bool:
    """Determine if the current platform is Windows or not."""
    return _system() == "Windows"


def reconcile_platform(
    program: str, args: _List[str]
) -> _Tuple[str, _List[str]]:
    """
    Handle arguments for Windows. You cannot run a program directly on Windows
    under any circumstance, so pass arguments through to the shell.
    """

    args = ["/c", program] + args if is_windows() else args
    program = "cmd.exe" if is_windows() else program
    return program, args


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
    ) -> _Process:
        """
        Create a process using subprocess exec and log what the arguments were.
        """

        exec_args = [x for x in args.split(separator) + [*caller_args] if x]
        self.log.info("exec '%s': %s", program, " ".join(exec_args))
        program, exec_args = reconcile_platform(program, exec_args)
        proc = await create_subprocess_exec(
            program,
            *exec_args,
            stdout=stdout,
            stderr=stderr,
        )
        return proc

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

        proc = await self.subprocess_exec(
            program,
            *caller_args,
            args=args,
            separator=separator,
            stdout=stdout,
            stderr=stderr,
        )
        await proc.communicate()
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

        command = cmd + joiner.join(
            x for x in args.split(separator) + [*caller_args] if x
        )
        self.log.info("shell: '%s'", command)
        proc = await create_subprocess_shell(
            command, stdout=stdout, stderr=stderr
        )
        return proc

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

        proc = await self.subprocess_shell(
            cmd,
            *caller_args,
            args=args,
            joiner=joiner,
            separator=separator,
            stdout=stdout,
            stderr=stderr,
        )
        await proc.communicate()
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

        proc = await self.subprocess_exec(
            program,
            *caller_args,
            args=args,
            separator=separator,
            stdout=_PIPE,
            stderr=_PIPE,
        )
        stdout, stderr = await proc.communicate()
        outbox["stdout"] = stdout
        outbox["stderr"] = stderr
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

        proc = await self.subprocess_exec(
            program, *caller_args, args=args, separator=separator
        )
        await proc.communicate()
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

        proc = await self.subprocess_shell(
            cmd,
            *caller_args,
            args=args,
            joiner=joiner,
            separator=separator,
            stdout=_PIPE,
            stderr=_PIPE,
        )
        stdout, stderr = await proc.communicate()
        outbox["stdout"] = stdout
        outbox["stderr"] = stderr
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

        proc = await self.subprocess_shell(
            cmd, *caller_args, args=args, joiner=joiner, separator=separator
        )
        await proc.communicate()
        outbox["code"] = proc.returncode

        return True if not require_success else proc.returncode == 0
