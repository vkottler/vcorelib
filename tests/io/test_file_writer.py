"""
Test the 'io.file_writer' module.
"""

# built-in
from io import StringIO
from os import linesep

# module under test
from vcorelib.io.file_writer import IndentedFileWriter


def test_file_writer_basic():
    """Test basic interactions with the indented file-writer."""

    with IndentedFileWriter.temporary() as writer:
        writer.write("Hello, world!")

    with IndentedFileWriter.string() as writer:
        writer.write("Hello, world!")

    with StringIO() as stream:
        writer = IndentedFileWriter(stream)
        writer.write("Hello, world!")

        # Check output.
        assert stream.getvalue() == "Hello, world!" + linesep

    with StringIO() as stream:
        writer = IndentedFileWriter(stream)
        writer.indent()
        writer.write("Hello, world!")

        # Check output.
        assert stream.getvalue() == " Hello, world!" + linesep

    with StringIO() as stream:
        writer = IndentedFileWriter(stream, per_indent=4)
        writer.dedent()
        writer.indent()
        writer.write("Hello, world!")

        # Check output.
        assert stream.getvalue() == "    Hello, world!" + linesep

        writer.dedent()
        writer.write("Hello, world!")

        assert (
            stream.getvalue()
            == "    Hello, world!" + linesep + "Hello, world!" + linesep
        )
