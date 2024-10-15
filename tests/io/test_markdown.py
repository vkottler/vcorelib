"""
Test the 'io.markdown' module.
"""

# module under test
from vcorelib.io import MarkdownMixin


def test_markdown_mixin_basic():
    """Test basic interactions with markdown mixin."""

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
