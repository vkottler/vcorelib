"""
A module for working with graph nodes.
"""

# built-in
from io import StringIO as _StringIO
from typing import TextIO as _TextIO
from typing import Type as _Type

# internal
from vcorelib.graph.abc import AbstractDiGraphNode as _AbstractDiGraphNode
from vcorelib.graph.abc import T as _T
from vcorelib.graph.abc import V as _V
from vcorelib.graph.edge import write_attributes as _write_attributes
from vcorelib.graph.edge import write_node_id as _write_node_id


class DiGraphNode(_AbstractDiGraphNode):
    """A base implementation for a directed-graph node."""

    def to_stream(self, stream: _TextIO, **kwargs) -> None:
        """Write this object to a text stream."""

        _write_node_id(self.label, stream, port=self.port)

        if "label" not in self.node_attributes:
            label_parts = [self.label]
            with _StringIO() as label_stream:
                self.ports.label(label_stream)
                label_parts.append(label_stream.getvalue())
            self.node_attributes["label"] = "|".join(label_parts)

        _write_attributes(stream, data=self.node_attributes)

        stream.write(";")

    def add_child(
        self,
        label: str,
        node: _T = None,
        graph_kind: _Type[_V] = None,
        **kwargs,
    ) -> _T:
        """
        Add an edge between this node (source) and the other node
        (destination).
        """

        graph = self.graph(kind=graph_kind)

        # Ensure the other node is a vertex in the graph.
        node = graph.handle_node(label, node=node)
        graph.add_edge(self.label, node.label, **kwargs)
        return node

    def add_parent(
        self,
        label: str,
        node: _T = None,
        graph_kind: _Type[_V] = None,
        **kwargs,
    ) -> _T:
        """
        Add an edge between this node (destination) and the other node
        (source).
        """

        graph = self.graph(kind=graph_kind)

        # Ensure the other node is a vertex in the graph.
        node = graph.handle_node(label, node=node)
        graph.add_edge(node.label, self.label, **kwargs)
        return node

    def add_parallel(
        self,
        label: str,
        node: _T = None,
        graph_kind: _Type[_V] = None,
        **kwargs,
    ) -> _T:
        """
        Add a parallel edge between two nodes. This instance is used as
        'node1'.
        """

        graph = self.graph(kind=graph_kind)

        # Ensure the other node is a vertex in the graph.
        node = graph.handle_node(label, node=node)
        graph.add_parallel(self.label, node.label, **kwargs)
        return node
