"""
A module for implementing namespaces.
"""

# built-in
from contextlib import contextmanager as _contextmanager
from typing import Iterator as _Iterator
from typing import List as _List

DEFAULT_DELIM = "."


class Namespace:
    """A class for implementing a basic namespace interface."""

    def __init__(self, *names: str, delim: str = DEFAULT_DELIM) -> None:
        """Initialize this namespace."""

        self.stack: _List[str] = [*names]
        self.delim = delim

        # Use this attribute from preventing this namespace from colliding with
        # its parent namespace.
        self.root_size = len(self.stack)

    def child(self, *names: str) -> "Namespace":
        """Create a child namespace from this one."""
        return Namespace(*self.stack, *names, delim=self.delim)

    def push(self, name: str) -> None:
        """Push a name onto the stack."""
        self.stack.append(name)

    def pop(self, name: str = None) -> str:
        """Pop the latest name off the stack."""

        # Ensure that the namespace can't be traversed beyond its
        # initialization path.
        curr_size = len(self.stack)
        if curr_size <= self.root_size:
            raise IndexError(
                (
                    f"Root namespace has {self.root_size} and this "
                    f"namespace currently has {curr_size}!"
                )
            )

        val = self.stack.pop()

        assert (
            val == name if name is not None else True
        ), f"'{val}' != '{name}'!"
        return val

    @_contextmanager
    def pushed(self, *names: str) -> _Iterator[None]:
        """
        Provide this namespace with some names pushed onto the stack as a
        context.
        """

        to_push = [*names]
        for name in to_push:
            self.push(name)

        yield

        for name in reversed(to_push):
            self.pop(name=name)

    def namespace(self, name: str = None, delim: str = None) -> str:
        """
        Get the current namespace string with or without an additional name
        applied.
        """
        if delim is None:
            delim = self.delim

        # Skip empty names.
        result = delim.join(x for x in self.stack if x)

        if name is not None:
            if result:
                result += delim
            result += name
        return result


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

    def push_name(self, name: str, namespace: Namespace = None) -> None:
        """Push a name onto the stack."""

        self._normalize_namespace(namespace=namespace).push(name)

    def pop_name(self, name: str = None, namespace: Namespace = None) -> str:
        """Pop the latest name off the stack."""

        return self._normalize_namespace(namespace=namespace).pop(name=name)
