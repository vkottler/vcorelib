"""
vcorelib - Test the 'dict' module.
"""

# internal
from copy import deepcopy
from typing import List

# module under test
from vcorelib.dict import (
    GenericDict,
    MergeStrategy,
    merge,
    merge_dicts,
    set_if_not,
)


def test_merge_bad_overwrite():
    """Test that if we don't want to overwrite, we don't."""

    dict_a: GenericDict = {}
    assert set_if_not(dict_a, "a", "a") == "a"
    dict_b: GenericDict = {}
    assert set_if_not(dict_b, "a", "b") == "b"

    assert merge(dict_a, dict_b) == dict_a
    assert merge(dict_a, dict_b, expect_overwrite=True) == dict_b


def test_merge_update():
    """Test the 'update' strategy of dictionary merges."""
    assert merge({"a": 1}, {"a": 2}, strategy=MergeStrategy.UPDATE) == {"a": 2}


def test_merge_basic():
    """Test the dictionary 'merge' functions."""

    starter = {"a": {"b": [1]}, "b": 1}

    def get_test_dict() -> List[dict]:
        """Get a list of dictionaries to merge."""

        return [
            deepcopy(starter),
            {"a": {"b": [2]}, "b": "2"},
            {"a": {"b": [3]}, "b": 2, "c": 3},
            {"a": {"b": [4]}, "b": "asdf"},
        ]

    assert merge_dicts(get_test_dict(), expect_overwrite=True) == {
        "a": {"b": [1, 2, 3, 4]},
        "b": 2,
        "c": 3,
    }
    assert merge_dicts(get_test_dict()) == {
        "a": {"b": [1, 2, 3, 4]},
        "b": 1,
        "c": 3,
    }
