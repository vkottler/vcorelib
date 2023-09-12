"""
Test the 'namespace' module.
"""

# third-party
from pytest import raises

# module under test
from vcorelib.namespace import CPP_DELIM, Namespace, NamespaceMixin


def test_namespace_parent_search():
    """Test that search recursion works."""

    root = Namespace(delim=CPP_DELIM)
    root.push("A")

    ns_b = root.child("B")

    root.namespace("C")

    assert list(ns_b.search(pattern="C")) == ["A::C"]
    assert not list(ns_b.search(pattern="C", recursive=False))


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
        assert inst.namespace("d.e") == "a.b.c.d.e"
    assert inst.namespace("d") == "d"
    inst.push_name("a")
    assert inst.pop_name("a") == "a"

    assert sorted(
        list(inst.namespace_search("a", "b", "c", pattern="d"))
    ) == sorted(
        [
            "a.b.c.d",
            "a.b.c.d.e",
        ]
    )

    assert inst.namespace_suggest("a.b") == ".c"
    assert inst.namespace_suggest("a.b.c") is None
    assert inst.namespace_suggest("a.b.c.") == "d"


def test_namespace_search_two():
    """Test that we can search namespaces for names."""

    names = Namespace(delim=CPP_DELIM)
    for name in [
        "uint8",
        "uint16",
        "uint32",
        "uint64",
        "int8",
        "int16",
        "int32",
        "int64",
    ]:
        names.namespace(name=name)

    assert list(names.search(pattern="int8", exact=True)) == ["int8"]


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
