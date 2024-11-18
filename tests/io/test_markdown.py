"""
Test the 'io.markdown' module.
"""

# internal
from tests.resources import get_test_schemas

# module under test
from vcorelib.io import MarkdownMixin
from vcorelib.io.markdown import default_markdown
from vcorelib.io.types import JsonObject
from vcorelib.schemas.mixins import SchemaMixin


def test_markdown_mixin_basic():
    """Test basic interactions with markdown mixin."""

    assert default_markdown()

    inst = MarkdownMixin()
    inst.set_markdown()
    assert inst.markdown

    schemas = get_test_schemas()

    class Subclass(MarkdownMixin, SchemaMixin):
        """Declare a sub-class."""

        data: JsonObject = {"a": "test", "b": {}}

    new_inst = Subclass(schemas)
    new_inst.set_markdown(config=Subclass.data)
    assert new_inst.markdown

    # print(new_inst.markdown)
    # assert False

    new_inst = Subclass(schemas)
    new_inst.set_markdown(package="tests")
    assert new_inst.markdown


def test_markdown_mixin_inheritance():
    """Test inheriting documentation pieces."""

    class SampleA(MarkdownMixin):
        """A sample class."""

    class SampleB(SampleA):
        """A sample class."""

    class SampleC(SampleB):
        """A sample class."""

    inst = SampleC()
    inst.set_markdown(
        markdown="instance-specific stuff 1",
        config={"markdown": "instance-specific stuff 2"},
        package="tests",
    )

    # print("==========")
    # print(inst.markdown)
    # print("==========")
    # assert False

    assert inst.markdown
