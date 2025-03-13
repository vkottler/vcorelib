"""
A module for working with paths to python interpreters and virtual
environments.
"""

# built-in
from os import environ as _environ
from pathlib import Path as _Path
from shutil import which as _which
from sys import executable as _executable
from sys import version_info as _version_info
from typing import NamedTuple

# internal
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize as _normalize

# third-party
from vcorelib.task.subprocess.run import is_windows as _is_windows

CURRENT_PYTHON = f"{_version_info[0]}.{_version_info[1]}"


def python_version() -> str:
    """Get the version of Python to use."""
    return _environ.get("PYTHON_VERSION", CURRENT_PYTHON)


def python_entry(version: str = None) -> str:
    """Attempt to get a Python entry-point as a string."""

    result = None

    if version is None:
        version = python_version()

    options = [f"python{version}{'.exe' if _is_windows() else ''}"]

    # Use the current executable as a candidate if it's the right version.
    if version.startswith(CURRENT_PYTHON):
        result = str(_executable)
        options.append(result)

    for option in options:
        if _which(option) is not None:
            result = option
            break

    assert result is not None, f"Couldn't find 'python{version}'!"
    return result


def venv_name(version: str = None) -> str:
    """Get the name for a virtual environment to use."""
    if version is None:
        version = python_version()
    return f"venv{version}"


def venv_dir(cwd: _Pathlike, version: str = None) -> _Path:
    """Get the path for a virtual environment to use."""
    return _normalize(cwd).joinpath(venv_name(version))


def venv_bin(
    cwd: _Pathlike, program: str = None, version: str = None
) -> _Path:
    """Get the path to a virtual environment's script directory."""

    path = venv_dir(cwd, version).joinpath(
        "Scripts" if _is_windows() else "bin"
    )
    if program is not None:
        path = path.joinpath(f"{program}{'.exe' if _is_windows() else ''}")
    return path


class StrToBool(NamedTuple):
    """A container for results when converting strings to boolean."""

    result: bool
    valid: bool

    def __bool__(self) -> bool:
        """Determine boolean status."""
        return self.result and self.valid

    @staticmethod
    def check(data: str) -> bool:
        """Check a string for a boolean 'true' value."""
        return bool(StrToBool.parse(data))

    @staticmethod
    def parse(data: str) -> "StrToBool":
        """Parse a string to boolean."""

        data = data.lower()
        is_true = data == "true"
        resolved = is_true or data == "false"
        return StrToBool(is_true, resolved)
