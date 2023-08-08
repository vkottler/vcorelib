"""
A module implementing an interface for writing to variably indented files.
"""

# from contextlib import contextmanager


class IndentedFileWriter:
    """A class for writing lines to a file and tracking indentation."""

    def __init__(self, indentation=" ") -> None:
        """Initialize this instance."""

        self.space = " "
        self.level = 0
        self.indentation = indentation

    def method_1(self) -> None:
        """helper method could be created to to create an IndentedFileWriter
        from a path to a file (probably a context manager.)"""

    def method_2(self) -> None:
        """method taking the str data for a new line of text to write
        to the file: first writes the indent (some number of
        e.g. space characters), then writes the str data (function parameter),
        then writes a newline character (os.linesep)."""

    def indent(self) -> None:
        """TODO."""
        self.level += 1

    def dedent(self) -> None:
        """TODO."""
        if self.level > 0:
            self.level -= 1
