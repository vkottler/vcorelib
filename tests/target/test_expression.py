"""
Test the 'target.expression' module.
"""

# module under test
from vcorelib.target import Target
from vcorelib.target.expression import ExpressionTarget


def test_expression_target_basic():
    """Test basic interactions with an expression target."""

    target = Target("a:{a},b:{b},c:{c}")
    expression = ExpressionTarget("sum-{a + b + c}")

    assert expression.compile_match(target, "a:1,b:2,c:3") == "sum-123"

    expression = ExpressionTarget("sum-{int(a) + int(b) + int(c)}")

    assert expression.compile_match(target, "a:1,b:2,c:3") == "sum-6"

    assert ExpressionTarget("literal-target")
