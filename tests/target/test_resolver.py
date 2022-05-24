"""
Test the 'target.resolver' module.
"""

# module under test
from vcorelib.target.resolver import TargetResolver


def test_resovler_basic():
    """Test basic interactions with a target resolver."""

    resolver = TargetResolver()
    resolver.register("test")
    resolver.register("a:{a}")
    resolver.register("b:{b}")
    resolver.register("c:{c}")

    assert resolver.evaluate("test")
    assert resolver.evaluate("a:1")
    assert not resolver.evaluate("d:4")
