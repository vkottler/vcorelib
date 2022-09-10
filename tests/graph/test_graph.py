"""
Test the 'graph' module.
"""

# module under test
from vcorelib.graph import DiGraph, DiGraphNode
from vcorelib.graph.edge import GraphEdge
from vcorelib.graph.port import PortType
from vcorelib.paths.context import tempfile


def add_sample_ports(node: DiGraphNode, count: int = 3) -> DiGraphNode:
    """Add sample ports to graph nodes."""

    for i in range(count):
        node.add_port(f"in{i}", kind=PortType.INPUT)
        node.add_port(f"out{i}", kind=PortType.OUTPUT)
        assert str(
            node.add_port(f"inout{i}", kind=PortType.INOUT, alias=f"io{i}")
        )

    # Add two extra outputs.
    for i in range(2):
        node.add_port(f"out{count + i}", kind=PortType.OUTPUT)

    return node


def test_graph_edge_basic():
    """Test basic interactions with graph edges."""

    assert GraphEdge("a", "b") == GraphEdge("a", "b")


def test_digraph_basic():
    """Test basic interactions with a directed graph."""

    graph = DiGraph(
        "test",
        graph_attrs={"color": "bisque"},
        node_attrs={"shape": "record"},
        edge_attrs={"color": "cyan"},
    )
    assert graph.default_location()

    # Set up some nodes for the graph.
    add_sample_ports(graph.add_vertex("a", DiGraphNode(color="red")))
    add_sample_ports(graph.add_vertex("b", DiGraphNode(color="blue")))
    add_sample_ports(graph.add_vertex("c", DiGraphNode(color="green")))

    # Add parallel edges between 'a' and 'b'.
    graph.add_parallel(
        "a",
        "b",
        src_port1="out0",
        dst_port1="in0",
        src_port2="inout0",
        dst_port2="inout0",
        arrowhead="diamond",
    )
    assert graph.is_parallel("a", "b")

    # Add directed edges.
    graph.add_edge("a", "c", src_port="out1", dst_port="in0", style="dotted")
    graph.add_edge("b", "c", src_port="out0", dst_port="in1", style="dotted")

    assert graph["b"] in set(graph["a"].outgoing())
    assert graph["a"] in set(graph["b"].incoming())

    assert graph["b"] in graph["a"].parallel()
    assert graph["a"] in graph["b"].parallel()

    assert graph["c"] not in graph["a"].parallel()
    assert graph["c"] not in graph["b"].parallel()

    # Verify serialization.
    with tempfile() as tmp:
        graph.to_file(tmp)
