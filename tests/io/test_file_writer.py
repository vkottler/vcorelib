"""
Test the 'io.file_writer' module.
"""

# built-in
from io import StringIO
from os import linesep

# module under test
from vcorelib.io.file_writer import IndentedFileWriter


def lines(*parts: str) -> str:
    """Get a sequence of strings as lines."""
    return linesep.join(parts) + linesep


def test_file_writer_scope():
    """Test various programming-language scoping invocations."""

    with StringIO() as stream:
        writer = IndentedFileWriter(stream, per_indent=4)
        with writer.scope(prefix="struct MyStruct ", suffix=";"):
            writer.c_comment("A comment.")
            writer.c_comment("Another comment.")

        assert stream.getvalue() == lines(
            "struct MyStruct {",
            "    /* A comment. */",
            "    /* Another comment. */",
            "};",
        )

    with StringIO() as stream:
        writer = IndentedFileWriter(stream, per_indent=4)
        with writer.indented():
            with writer.javadoc():
                writer.write("A comment.")
                writer.write("Another comment.")

            with writer.scope():
                writer.cpp_comment("Yup.")

        assert stream.getvalue() == lines(
            "    /**",
            "     * A comment.",
            "     * Another comment.",
            "     */",
            "    {",
            "        // Yup.",
            "    }",
        )


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

        with writer.indented():
            writer.write("Hello, world!")

        # Check output.
        assert stream.getvalue() == "    Hello, world!" + linesep

        writer.write("Hello, world!")

        assert (
            stream.getvalue()
            == "    Hello, world!" + linesep + "Hello, world!" + linesep
        )
