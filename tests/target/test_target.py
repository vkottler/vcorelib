"""
Test the 'target' module.
"""

# module under test
from vcorelib.target import Target


def test_target_basic():
    """Test basic interactions with target objects."""

    target = Target("test")
    assert target == Target("test")
    assert target.literal
    match_data = target.evaluate("test")
    assert match_data.matched is True
    assert target.evaluate("not_test").matched is False

    target = Target("{test}")
    assert not target.literal
    match_data = target.evaluate("test")
    assert match_data.matched is True
    assert match_data.get("test") == "test"

    target = Target("a:{a},b:{b},c:{c}")
    match_data = target.evaluate("a:1,b:2,c:3")
    assert int(match_data.get("a")) == 1
    assert int(match_data.get("b")) == 2
    assert int(match_data.get("c")) == 3
    assert target.evaluate("a:1,b:2,c:3,d:4").matched is False


def test_target_compile():
    """Verify we can compile a target from input data."""

    target = Target("a:{a},b:{b},c:{c}")

    evaluator = target.evaluator
    assert evaluator is not None

    assert evaluator.compile({"a": 1, "b": 2, "c": 3}) == "a:1,b:2,c:3"


def test_target_with_dot():
    """Test for bugs and other parsing/compiling scenarios."""

    in_target = Target("asdf.{test}")
    out_target = Target("1234.{test}")

    match = in_target.evaluate("asdf.1234")
    assert match.matched
    assert match.substitutions is not None

    assert out_target.compile(substitutions=match.substitutions) == "1234.1234"

    in_target = Target("{test}.asdf")
    out_target = Target("{test}.1234")

    match = in_target.evaluate("1234.asdf")
    assert match.matched
    assert match.substitutions is not None

    print(out_target.evaluator)
    assert out_target.compile(substitutions=match.substitutions) == "1234.1234"
