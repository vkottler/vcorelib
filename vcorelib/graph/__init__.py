"""
A module for implementing graph-like data structures.

See Graphviz's 'DOT Language' here: https://graphviz.org/doc/info/lang.html.
"""

# built-in
from collections import UserDict
from io import StringIO
from os import linesep as _linesep
from typing import Dict, Iterator, Set
from typing import TextIO as _TextIO
from typing import TypeVar

# internal
from vcorelib import DEFAULT_INDENT
from vcorelib.graph.edge import (
    AttributeMap,
    GraphEdge,
    write_attributes,
    write_node_id,
)
from vcorelib.graph.port import Port, PortManager
from vcorelib.io.abc import Serializable

T = TypeVar("T", bound="DiGraphNode")
V = TypeVar("V", bound="DiGraph")


def write_indent(
    indent: int, stream: _TextIO, linesep: str = _linesep
) -> None:
    """Handle indented prefixes for new lines in a text stream."""

    if indent > 0:
        if linesep:
            stream.write(linesep)
        stream.write(" " * indent)


class DiGraphNode(Serializable):
    """A base class for a directed-graph node."""

    def __init__(
        self, graph: V = None, label: str = None, port: Port = None, **attrs
    ) -> None:
        """Initialize this graph node."""

        self._graph = graph
        self._label = label
        self.port = port
        self.node_attributes = {**attrs}
        self.ports = PortManager()

    def add_port(self, label: str, **kwargs) -> Port:
        """Add a port to this graph node."""
        return self.ports.create(label, **kwargs)

    def allocate_port(self, label: str) -> Port:
        """Allocate a port on this node."""
        return self.ports.allocate(label)

    def to_stream(self, stream: _TextIO, **kwargs) -> None:
        """Write this object to a text stream."""

        write_node_id(self.label, stream, port=self.port)

        if "label" not in self.node_attributes:
            label_parts = [self.label]
            with StringIO() as label_stream:
                self.ports.label(label_stream)
                label_parts.append(label_stream.getvalue())
            self.node_attributes["label"] = "|".join(label_parts)

        write_attributes(stream, data=self.node_attributes)

        stream.write(";")

    @property
    def graph(self) -> V:
        """Get the graph that this node belongs to."""
        assert self._graph is not None, "Node hasn't joined a graph!"
        return self._graph

    @property
    def label(self) -> str:
        """Get this node's label."""
        assert self._label is not None, "Node hasn't joined a graph!"
        return self._label

    def join_graph(self, graph: V, label: str) -> None:
        """Attempt to join a graph."""

        # Verify the graph assignment.
        assert (
            self._graph is None or self._graph is graph
        ), f"Node '{self}' is already part of a different graph!"

        # Verify the label assignment.
        assert (
            self._label is None or self._label == label
        ), f"Node already has label '{self._label}' (!= '{label}')!"

        self._graph = graph
        self._label = label

    def outgoing(self) -> Iterator[T]:
        """Iterate over nodes that we have outgoing edges to."""

        for edge in self.graph.edges[self.label]:
            yield self.graph[edge.dst]

    def incoming(self) -> Iterator[T]:
        """Iterate over nodes that have incoming edges."""

        for label, edges in self.graph.edges.items():
            for edge in edges:
                if self.label == edge.dst:
                    yield self.graph[label]
                    break

    def parallel(self) -> Set[T]:
        """Iterate over nodes that this instance shares parallel edges with."""

        outgoing: Set[T] = set(self.outgoing())
        incoming: Set[T] = set(self.incoming())
        return outgoing.intersection(incoming)


class DiGraph(UserDict, Serializable):
    """A simple, directed-graph implementation."""

    def __init__(
        self,
        name: str,
        initialdata: Dict[str, T] = None,
        graph_attrs: AttributeMap = None,
        node_attrs: AttributeMap = None,
        edge_attrs: AttributeMap = None,
    ) -> None:
        """Initialize this graph."""

        self.name = name
        super().__init__(initialdata)
        self.graph_attrs = graph_attrs
        self.node_attrs = node_attrs
        self.edge_attrs = edge_attrs

        # Source node -> a set of all destination edges.
        self.edges: Dict[str, Set[GraphEdge]] = {}

    def to_stream(self, stream: _TextIO, **kwargs) -> None:
        """Write this object to a text stream."""

        indent: int = kwargs.pop("indent", DEFAULT_INDENT)
        linesep: str = kwargs.pop("linesep", _linesep)

        stream.write(f"strict digraph {self.name} {{")

        # Add top-level graph attributes.
        if self.graph_attrs:
            write_indent(indent, stream, linesep=linesep)
            stream.write("graph")
            write_attributes(stream, data=self.graph_attrs)

        # Add top-level node attributes.
        if self.node_attrs:
            write_indent(indent, stream, linesep=linesep)
            stream.write("node")
            write_attributes(stream, data=self.node_attrs)

        # Add top-level edge attributes.
        if self.edge_attrs:
            write_indent(indent, stream, linesep=linesep)
            stream.write("edge")
            write_attributes(stream, data=self.edge_attrs)

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

    def add_vertex(self, label: str, node: T) -> T:
        """Add a vertext to the graph."""

        assert label not in self.data, f"Duplicate label '{label}'!"

        # Add a reference for the graph node to the graph itself.
        node.join_graph(self, label)

        # Add the node to the graph.
        self.data[label] = node
        self.edges[label] = set()
        return node

    def add_edge(
        self,
        src: str,
        dst: str,
        src_port: str = None,
        dst_port: str = None,
        strict: bool = False,
        **attrs,
    ) -> None:
        """Add an edge between nodes in the graph."""

        assert src in self.data, f"Source vertex '{src}' not in graph!"
        assert dst in self.data, f"Destination vertex '{dst}' not in graph!"

        # Allocate a source port if a label was provided.
        sport = None
        if src_port:
            sport = self.data[src].allocate_port(src_port)

            # Verify the source port is an output.
            assert (
                sport.is_output
            ), f"Source port '{sport}' ('{src}') is not an output!"

        # Allocate a destination port if a label was provided.
        dport = None
        if dst_port:
            dport = self.data[dst].allocate_port(dst_port)

            # Verify the destination port is an input.
            assert (
                dport.is_input
            ), f"Destination port '{dport}' ('{dst}') is not an input!"

        edge = GraphEdge(
            src, dst, src_port=sport, dst_port=dport, attrs={**attrs}
        )
        edges = self.edges[src]

        # Prevent adding duplicate edges if desired.
        assert (
            not strict or edge not in edges
        ), f"Edge '{src}' -> '{dst}' already present!"

        edges.add(edge)

    def add_parallel(
        self,
        node1: str,
        node2: str,
        src_port1: str = None,
        dst_port1: str = None,
        src_port2: str = None,
        dst_port2: str = None,
        **kwargs,
    ) -> None:
        """Add an edge in each direction for two nodes."""

        self.add_edge(
            node1, node2, src_port=src_port1, dst_port=dst_port1, **kwargs
        )
        self.add_edge(
            node2, node1, src_port=src_port2, dst_port=dst_port2, **kwargs
        )

    def is_parallel(self, node1: str, node2: str) -> bool:
        """Determine if parallel edges exist between two nodes."""

        success = node1 in self.data and node2 in self.data

        if success:
            success = False

            # Check if we have a destination edge to node1 from node2.
            for edge in self.edges[node1]:
                if edge.dst == node2:
                    success = True
                    break

            if success:
                success = False

                # Check if we have a destination edge to node2 from node1.
                for edge in self.edges[node2]:
                    if edge.dst == node1:
                        success = True
                        break

        return success
