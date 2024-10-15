"""
A module implementing markdown-specific interfaces.
"""

# built-in
from contextlib import suppress
from functools import cache
from pathlib import Path
from typing import Optional

# internal
from vcorelib import DEFAULT_ENCODING, PKG_NAME
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import resource


@cache
def cached_read_file(path: Path) -> str:
    """Read file contents."""

    with path.open("r", encoding=DEFAULT_ENCODING) as default:
        result = default.read()
    return result


def read_resource(
    *args, package: str = PKG_NAME, strict: bool = True, **kwargs
) -> str:
    """Read resource contents."""

    path = resource(*args, **kwargs, package=package, strict=strict)
    assert path is not None
    return cached_read_file(path)


@cache
def default_markdown() -> str:
    """Get default markdown contents."""

    return read_resource("md", "MarkdownMixin.md")


class MarkdownMixin:
    """A simple markdown class mixin."""

    markdown: str

    @classmethod
    def class_markdown(cls, **kwargs) -> Optional[str]:
        """Attempt to get markdown for this class."""

        result = None

        # Search for documentation for this class.
        with suppress(AssertionError):
            result = read_resource("md", f"{cls.__name__}.md", **kwargs)

        # Search the class hierarchy for documentation.
        if result is None and cls.__bases__:
            for base in cls.__bases__:
                if hasattr(base, "class_markdown"):
                    result = base.class_markdown(**kwargs)
                if result:
                    break

        return result

    def set_markdown(
        self, markdown: str = None, config: _JsonObject = None, **kwargs
    ) -> None:
        """Set markdown for this instance."""

        assert not hasattr(self, "markdown")

        self.markdown: str = (
            markdown  # type: ignore
            or (None if config is None else config.get("markdown"))
            or self.class_markdown(**kwargs)
            or default_markdown()
        )
