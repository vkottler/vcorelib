"""
Test the 'dict.config' module.
"""

# built-in
from os.path import join

# internal
from tests.resources import resource

# module under test
from vcorelib.dict.config import Config


def test_dict_config_basic():
    """Test basic interactions with a config object."""

    config = Config({"a": 1})
    assert config["a"] == 1
    assert config.get("b") is None
    config.set_if_not("a", 2)
    assert config["a"] == 2
    config.merge({"b": 3})

    assert config.from_path(resource(join("simple_decode", "json")))["a"]
    assert config.from_path(resource(join("simple_decode", "a")))["a"]
    assert config.from_path(resource(join("simple_decode", "d.yaml")))["e"]
