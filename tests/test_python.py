"""
Test the 'python' module.
"""

# module under test
from vcorelib.python import StrToBool, python_entry, venv_bin


def test_python_methods_basic():
    """Test basic interactions with python-module methods."""

    assert venv_bin(".")
    assert venv_bin(".", program="python")
    assert venv_bin(".", version="3.11")
    assert venv_bin(".", version="3.11", program="python")
    assert python_entry()


def test_str_to_bool_basic():
    """Test basic string to boolean conversions."""

    assert StrToBool.parse("true").result
    assert StrToBool.parse("false").valid

    assert StrToBool.check("true")
    assert StrToBool.check("TRUE")
