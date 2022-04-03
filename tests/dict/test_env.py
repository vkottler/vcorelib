"""
vcorelib - Test the 'dict.env' module.
"""

# built-in
from os import environ

# module under test
from vcorelib.dict.env import (
    dict_resolve_env_vars,
    list_resolve_env_vars,
    str_resolve_env_var,
)


def test_resolve_env_vars():
    """
    Test that we can correctly resolve environment variables in data
    structures.
    """

    environ["TEST"] = "test"
    assert str_resolve_env_var("$TEST") == "test"
    assert list_resolve_env_vars(["$TEST", ["$TEST"], {"$TEST": "$TEST"}]) == [
        "test",
        ["test"],
        {"test": "test"},
    ]
    assert dict_resolve_env_vars({"a": {"b": ["$TEST"]}}) == {
        "a": {"b": ["test"]}
    }
