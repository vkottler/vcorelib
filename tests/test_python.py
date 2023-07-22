"""
Test the 'python' module.
"""

# module under test
from vcorelib.python import python_entry, venv_bin


def test_python_methods_basic():
    """Test basic interactions with python-module methods."""

    assert venv_bin(".")
    assert venv_bin(".", program="python")
    assert venv_bin(".", version="3.11")
    assert venv_bin(".", version="3.11", program="python")
    assert python_entry()
