"""
A module implementing markdown-specific interfaces.
"""

# built-in
from contextlib import suppress
from functools import cache
from os import linesep
from pathlib import Path
from typing import Iterator, Optional

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

    # This path gets hit even when reaching 'MarkdownMixin' due to the
    # singleton 'package' variable (only one package is searched)
    return read_resource("md", "default.md")


class MarkdownMixin:
    """A simple markdown class mixin."""

    markdown: str

    @classmethod
    def class_markdown_parts(
        cls, _visited: set[str] = None, **kwargs
    ) -> Iterator[str]:
        """Iterate over all documentation snippets."""

        if _visited is None:
            _visited = set()

        # Search for documentation for this class.
        name = cls.__name__
        if name not in _visited:
            with suppress(AssertionError):
                yield read_resource("md", f"{name}.md", **kwargs)
                _visited.add(name)

        # Search for parts in parents.
        for base in cls.__bases__:
            if hasattr(base, "class_markdown_parts"):
                yield from base.class_markdown_parts(
                    _visited=_visited, **kwargs
                )

    @classmethod
    def class_markdown(
        cls, _visited: set[str] = None, parts: list[str] = None, **kwargs
    ) -> Optional[str]:
        """Attempt to get markdown for this class."""

        result = None

        compiled = (linesep + linesep).join(
            (parts or [])
            + list(x.rstrip() for x in cls.class_markdown_parts(**kwargs))
        )
        if compiled:
            result = compiled

        return result

    def set_markdown(
        self, markdown: str = None, config: _JsonObject = None, **kwargs
    ) -> None:
        """Set markdown for this instance."""

        assert not hasattr(self, "markdown")

        parts = []
        if markdown:
            parts.append(markdown)
        if config and config.get("markdown"):
            parts.append(config["markdown"])  # type: ignore

        self.markdown: str = (
            self.class_markdown(parts=parts, **kwargs) or default_markdown()
        )
