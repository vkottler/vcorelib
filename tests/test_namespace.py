"""
Test the 'namespace' module.
"""

# third-party
from pytest import raises

# module under test
from vcorelib.namespace import Namespace, NamespaceMixin


def test_namespace_basic():
    """Test basic functionality of namespaces."""

    class NamespaceEntity(NamespaceMixin):
        """A sample class."""

    inst = NamespaceEntity()

    child = inst.child_namespace("test")
    with raises(IndexError):
        child.pop()

    with inst.names_pushed("a", "b", "c"):
        assert inst.namespace() == "a.b.c"
        assert inst.namespace("d") == "a.b.c.d"
    assert inst.namespace("d") == "d"
    inst.push_name("a")
    assert inst.pop_name("a") == "a"

    assert list(inst.namespace_search("a", "b", "c", pattern="d")) == [
        "a.b.c.d"
    ]


def test_namespace_search():
    """Test that we can search namespaces for names."""

    names = Namespace()

    sample = [f"name_{x}" for x in "abc"]
    for item in sample:
        names.namespace(name=item)

    assert sorted(list(names.search())) == sample
    assert sorted(list(names.search(pattern="name"))) == sample
    assert list(names.search(pattern="_a")) == ["name_a"]

    # Add names to a sepecific namespace.
    with names.pushed("test"):
        for item in sample:
            names.namespace(name=item)

    assert sorted(list(names.search(pattern="test"))) == [
        "test.name_a",
        "test.name_b",
        "test.name_c",
    ]

    assert sorted(list(names.search("test", pattern="name"))) == [
        "test.name_a",
        "test.name_b",
        "test.name_c",
    ]

    assert list(names.search("test", pattern="b")) == ["test.name_b"]
