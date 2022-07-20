"""
Test the 'namespace' module.
"""

# module under test
from vcorelib.namespace import NamespaceMixin


def test_namespace_basic():
    """Test basic functionality of namespaces."""

    class NamespaceEntity(NamespaceMixin):
        """A sample class."""

    inst = NamespaceEntity()
    with inst.names_pushed("a", "b", "c"):
        assert inst.namespace() == "a.b.c"
        assert inst.namespace("d") == "a.b.c.d"
    assert inst.namespace("d") == "d"
    inst.push_name("a")
    assert inst.pop_name("a") == "a"
