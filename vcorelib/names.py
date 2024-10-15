"""
Common name manipulations.
"""

# built-in
import re as _re
from typing import Any as _Any
from typing import Iterable, Iterator


def obj_class_to_snake(class_obj: _Any) -> str:
    """Convert a CamelCase named class to a snake_case String."""

    return to_snake(class_obj.__class__.__name__)


def to_snake(name: str, lower_dashes: bool = True) -> str:
    """Convert a CamelCase String to snake_case."""

    name = _re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    result = _re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
    if lower_dashes:
        result = result.replace("-", "_")
    return result


def name_search(
    names: Iterable[str], pattern: str, exact: bool = False
) -> Iterator[str]:
    """A simple name searching method."""

    compiled = _re.compile(pattern)
    for name in names:
        if compiled.search(name) is not None:
            if not exact or name == pattern:
                yield name


def import_str_and_item(module_path: str) -> tuple[str, str]:
    """
    Treat the last entry in a '.' delimited string as the item to import from
    the module in the string preceding it.
    """

    parts = module_path.split(".")
    assert len(parts) > 1, module_path

    item = parts.pop()
    return ".".join(parts), item
