"""
A module implementing markdown-specific interfaces.
"""

from contextlib import suppress

# built-in
from copy import copy
from functools import cache
from json import dumps
from os import linesep
from pathlib import Path
from typing import Iterator, Optional

# internal
from vcorelib import DEFAULT_ENCODING, PKG_NAME
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import resource
from vcorelib.schemas.mixins import SchemaMixin


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


def object_markdown(
    title: str, data: _JsonObject, indent: int = 4, **kwargs
) -> str:
    """Get markdown contents for object data."""

    return linesep.join(
        [title, "", "```", dumps(data, indent=indent, **kwargs), "```"]
    )


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
        self,
        *_parts: str,
        markdown: str = None,
        config: _JsonObject = None,
        schema_data: _JsonObject = None,
        config_instance_title: str = "# Instance Configuration",
        config_schema_title: str = "# Configuration Schema",
        **kwargs,
    ) -> None:
        """Set markdown for this instance."""

        assert not hasattr(self, "markdown")

        parts = list(_parts)
        if markdown:
            parts.append(markdown)

        if config:
            cloned = copy(config)

            # Instance markdonw.
            if cloned.get("markdown"):
                parts.append(cloned["markdown"])  # type: ignore
                del cloned["markdown"]

            # Configuration data.
            if cloned:
                parts.append(object_markdown(config_instance_title, cloned))

        # Possible schema component.
        if isinstance(self, SchemaMixin) and schema_data is None:
            schema_data = self.schema.data
        if schema_data:
            parts.append(object_markdown(config_schema_title, schema_data))

        self.markdown: str = (
            self.class_markdown(parts=parts, **kwargs) or default_markdown()
        )
