"""
A module for implementing graph-like data structures.

See Graphviz's 'DOT Language' here: https://graphviz.org/doc/info/lang.html.
"""

# built-in
from os import linesep as _linesep
from typing import TextIO as _TextIO

# internal
from vcorelib import DEFAULT_INDENT as _DEFAULT_INDENT
from vcorelib.graph.abc import AbstractDiGraph as _AbstractDiGraph
from vcorelib.graph.edge import write_attributes as _write_attributes


def write_indent(
    indent: int, stream: _TextIO, linesep: str = _linesep
) -> None:
    """Handle indented prefixes for new lines in a text stream."""

    if indent > 0:
        if linesep:
            stream.write(linesep)
        stream.write(" " * indent)


class DiGraph(_AbstractDiGraph):
    """A simple, directed-graph implementation."""

    def to_stream(self, stream: _TextIO, **kwargs) -> None:
        """Write this object to a text stream."""

        indent: int = kwargs.pop("indent", _DEFAULT_INDENT)
        linesep: str = kwargs.pop("linesep", _linesep)

        stream.write(f"strict digraph {self.name} {{")

        # Add top-level graph attributes.
        if self.graph_attrs:
            write_indent(indent, stream, linesep=linesep)
            stream.write("graph")
            _write_attributes(stream, data=self.graph_attrs)
            stream.write(";")

        # Add top-level node attributes.
        if self.node_attrs:
            write_indent(indent, stream, linesep=linesep)
            stream.write("node")
            _write_attributes(stream, data=self.node_attrs)
            stream.write(";")

        # Add top-level edge attributes.
        if self.edge_attrs:
            write_indent(indent, stream, linesep=linesep)
            stream.write("edge")
            _write_attributes(stream, data=self.edge_attrs)
            stream.write(";")

        # Write nodes.
        for node in self.data.values():
            write_indent(indent, stream, linesep=linesep)
            node.to_stream(stream)

        # Write edges.
        for edge_set in self.edges.values():
            for edge in edge_set:
                write_indent(indent, stream, linesep=linesep)
                edge.to_stream(stream)

        stream.write(linesep if indent > 0 else " ")
        stream.write("}")
