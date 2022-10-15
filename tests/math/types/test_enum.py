"""
Test the 'math.types.enum' module.
"""

# built-in
import ctypes

# module under test
from vcorelib.math.types.enum import PrimitiveTypes, normalize_type


def test_primitive_types_basic():
    """Test basic usages of the primitive-types enumeration."""

    assert PrimitiveTypes.INT8.value() == 0
    test_int = PrimitiveTypes.UINT8.value()
    test_int(256)
    assert test_int == 0
    assert test_int.kind.get_int().value == test_int

    test_float = PrimitiveTypes.FLOAT.value()
    assert test_float == 0.0
    assert test_float.kind.get_float().value == 0.0

    test_float(1.0)
    assert test_float == 1.0

    compare = False
    test_bool = PrimitiveTypes.BOOL.value()
    assert test_bool == compare
    assert test_bool.kind.get_bool().value == test_bool

    test_bool(True)
    compare = True
    assert test_bool == compare
    assert str(test_bool.kind) == "bool"
    assert test_bool.kind == ctypes.c_bool
    assert test_bool.kind == test_bool.kind
    assert hash(test_bool.kind)

    # Call all of the constructors.
    for _ in PrimitiveTypes:
        test_bool()

    test_bool = normalize_type("bool").value()
    test_bool(True)
    compare = True
    assert test_bool == compare

    for val in ["float", "double"]:
        test_float = normalize_type(val).value()
        test_float(1.0)
        assert test_float == 1.0

    for val in [
        "int8",
        "int16",
        "int32",
        "int64",
        "uint8",
        "uint16",
        "uint32",
        "uint64",
    ]:
        test_int = normalize_type(val).value()
        test_int(1)
        assert test_int == 1
