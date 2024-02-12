"""
A module implementing a simple namespace mixin class.
"""

# built-in
from contextlib import contextmanager as _contextmanager
from typing import Iterator as _Iterator
from typing import Optional as _Optional

# internal
from vcorelib.namespace.base import DEFAULT_DELIM, Namespace


class NamespaceMixin:
    """A class for giving arbitrary objects namespace capabilities."""

    def __init__(
        self, namespace: Namespace = None, namespace_delim: str = DEFAULT_DELIM
    ) -> None:
        """Initialize a namespace for this object."""

        if not hasattr(self, "_namespace"):
            if namespace is None:
                namespace = Namespace(delim=namespace_delim)
            self._namespace = namespace

    def _normalize_namespace(self, namespace: Namespace = None) -> Namespace:
        """Return this instance's namespace if one isn't provided."""

        if namespace is None:
            namespace = self._namespace
        return namespace

    @property
    def ns(self) -> Namespace:
        """Get this instance's namespace."""

        assert self._namespace is not None
        return self._namespace

    def namespace(
        self, name: str = None, delim: str = None, namespace: Namespace = None
    ) -> str:
        """Get a namespace string for this object."""

        return self._normalize_namespace(namespace=namespace).namespace(
            name=name, delim=delim
        )

    def child_namespace(
        self, *names: str, namespace: Namespace = None
    ) -> Namespace:
        """Obtain a child namespace."""

        return self._normalize_namespace(namespace=namespace).child(*names)

    @_contextmanager
    def names_pushed(
        self, *names: str, namespace: Namespace = None
    ) -> _Iterator[None]:
        """Apply some names to this object's namespace as a managed context."""

        with self._normalize_namespace(namespace=namespace).pushed(*names):
            yield

    def namespace_suggest(
        self, data: str, delta: bool = True, namespace: Namespace = None
    ) -> _Optional[str]:
        """Find the shortest name suggestion."""

        return self._normalize_namespace(namespace=namespace).suggest(
            data, delta=delta
        )

    def push_name(self, name: str, namespace: Namespace = None) -> None:
        """Push a name onto the stack."""

        self._normalize_namespace(namespace=namespace).push(name)

    def pop_name(self, name: str = None, namespace: Namespace = None) -> str:
        """Pop the latest name off the stack."""

        return self._normalize_namespace(namespace=namespace).pop(name=name)

    def namespace_search(
        self, *names: str, pattern: str = ".*", namespace: Namespace = None
    ) -> _Iterator[str]:
        """Perform a search on the namespace."""

        yield from self._normalize_namespace(namespace=namespace).search(
            *names, pattern=pattern
        )
