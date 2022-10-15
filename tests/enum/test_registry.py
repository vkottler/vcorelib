"""
Test the 'enum.registry' module.
"""

# internal
from tests.resources import resource

# module under test
from vcorelib.enum import EnumType
from vcorelib.enum.registry import EnumRegistry


def test_enum_registry_basic():
    """Test interactions with an enum registry."""

    assert str(EnumType.BOOL)

    test = EnumRegistry.decode(resource("enums", "sample_enum.yaml"))

    int1 = test.get_int("int1")
    bool1 = test.get_bool("bool1")

    assert test.enums["int1"].type.validate(1)

    assert int1.as_value("a") == 1
    assert int1.as_value(1) == 1
    assert int1.as_str(1) == "a"
    assert int1.as_str("a") == "a"

    assert bool1.as_value("valve_open") is True
    assert bool1.as_str(True) == "valve_open"

    int2 = test.register_int("int2")
    int2.add("a", 1)
    int2.add("b", 2)
    int2.add("c", 3)

    assert int1 == int2

    int3 = test.register_int("int3", reverse={1: "a", 2: "b", 3: "c"})
    assert int3 == int2

    bool2 = test.register_bool("bool2")
    bool2.add("on", True)
    bool2.add("off", False)
