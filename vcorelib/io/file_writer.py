"""
A module implementing an interface for writing to variably indented files.
"""

# built-in
from contextlib import contextmanager
from io import StringIO
from os import linesep
from pathlib import Path
from typing import Iterator, TextIO

# internal
from vcorelib import DEFAULT_ENCODING
from vcorelib.paths.context import tempfile


class IndentedFileWriter:
    """A class for writing lines to a file and tracking indentation."""

    def __init__(
        self, stream: TextIO, space: str = " ", per_indent: int = 1
    ) -> None:
        """Initialize this instance."""

        self.stream = stream
        self.space = space
        self.per_indent = per_indent
        self.depth = 0

    @staticmethod
    @contextmanager
    def from_path(
        path: Path, space: str = " ", per_indent: int = 1
    ) -> Iterator["IndentedFileWriter"]:
        """Create an instance from a path as a managed context."""

        with path.open("w", encoding=DEFAULT_ENCODING) as stream:
            yield IndentedFileWriter(
                stream, space=space, per_indent=per_indent
            )

    @staticmethod
    @contextmanager
    def string(
        space: str = " ", per_indent: int = 1
    ) -> Iterator["IndentedFileWriter"]:
        """Create an instance for a string."""

        with StringIO() as stream:
            yield IndentedFileWriter(
                stream, space=space, per_indent=per_indent
            )

    @staticmethod
    @contextmanager
    def temporary(
        space: str = " ", per_indent: int = 1
    ) -> Iterator["IndentedFileWriter"]:
        """Create an instance from a temporary file as a managed context."""

        with tempfile() as tmp:
            with IndentedFileWriter.from_path(
                tmp, space=space, per_indent=per_indent
            ) as writer:
                yield writer

    def method_1(self) -> None:
        """helper method could be created to to create an IndentedFileWriter
        from a path to a file (probably a context manager.)"""

    def write(self, data: str) -> int:
        """
        method taking the str data for a new line of text to write
        to the file: first writes the indent (some number of
        e.g. space characters), then writes the str data (function parameter),
        then writes a newline character (os.linesep).
        """

        data = (self.space * self.depth * self.per_indent) + data + linesep
        self.stream.write(data)
        return len(data)

    def indent(self, amount: int = 1) -> None:
        """Increase the current indent depth."""

        self.depth += amount

    def dedent(self, amount: int = 1) -> None:
        """Decrease the current indent depth (if not zero)."""

        if self.depth > 0 and amount <= self.depth:
            self.depth -= amount

    @contextmanager
    def indented(self, amount: int = 1) -> Iterator[None]:
        """Increase the current indent depth and decrease upon exit."""

        self.indent(amount=amount)
        try:
            yield
        finally:
            self.dedent(amount=amount)
