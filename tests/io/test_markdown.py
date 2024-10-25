"""
Test the 'io.markdown' module.
"""

# module under test
from vcorelib.io import MarkdownMixin
from vcorelib.io.markdown import default_markdown


def test_markdown_mixin_basic():
    """Test basic interactions with markdown mixin."""

    assert default_markdown()

    inst = MarkdownMixin()
    inst.set_markdown()
    assert inst.markdown

    class Subclass(MarkdownMixin):
        """Declare a sub-class."""

    new_inst = Subclass()
    new_inst.set_markdown()
    assert inst.markdown

    new_inst = Subclass()
    new_inst.set_markdown(package="tests")
    assert inst.markdown


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
