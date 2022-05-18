"""
Test the 'script' module.
"""

# built-in
from os.path import join

# internal
from tests.resources import resource

# module under test
from vcorelib.script import invoke_script
from vcorelib.task.manager import TaskManager


def test_invoke_script_basic():
    """Test that we can invoke an external script and get the result."""

    script = resource(join("scripts", "test.py"))
    assert invoke_script(script, "test", 1, 2, 3, four=4, five=5, six=6) == 21

    script_obj = TaskManager()
    assert script_obj.script(script, "test_obj", "a") == 0
    assert script_obj.invoked(script)
    assert script_obj.execute(["a"]) == set()
