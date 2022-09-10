"""
Test the 'graph.node' module.
"""

# module under test
from vcorelib.graph import DiGraph
from vcorelib.graph.node import DiGraphNode


def test_graph_node_edges():
    """Test the edge-adding methods of the di-graph node."""

    graph = DiGraph("test")
    node_a = graph.add_vertex("a", DiGraphNode())
    graph.add_vertex("b", DiGraphNode())
    node_a.add_child("b")
    node_a.add_parent("c", DiGraphNode())
    node_a.add_parallel("d", DiGraphNode())
