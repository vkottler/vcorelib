"""
A module for implementing namespaces.
"""

# built-in
from contextlib import contextmanager as _contextmanager
from typing import Iterator as _Iterator
from typing import List as _List


class Namespace:
    """A class for implementing a basic namespace interface."""

    def __init__(self, *names: str) -> None:
        """Initialize this namespace."""
        self.stack: _List[str] = [*names]

    def push(self, name: str) -> None:
        """Push a name onto the stack."""
        self.stack.append(name)

    def pop(self, name: str = None) -> str:
        """Pop the latest name off the stack."""

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
            self.pop(name)

    def namespace(self, name: str = None, delim: str = ".") -> str:
        """
        Get the current namespace string with or without an additional name
        applied.
        """
        result = delim.join(self.stack)
        if name is not None:
            if result:
                result += delim
            result += name
        return result


class NamespaceMixin:
    """A class for giving arbitrary objects namespace capabilities."""

    def __init__(self, namespace: Namespace = None) -> None:
        """Initialize a namespace for this object."""

        if not hasattr(self, "_namespace"):
            if namespace is None:
                namespace = Namespace()
            self._namespace = namespace

    def namespace(self, name: str = None, delim: str = ".") -> str:
        """Get a namespace string for this object."""
        return self._namespace.namespace(name=name, delim=delim)

    @_contextmanager
    def names_pushed(self, *names: str) -> _Iterator[None]:
        """Apply some names to this object's namespace as a managed context."""
        with self._namespace.pushed(*names):
            yield
