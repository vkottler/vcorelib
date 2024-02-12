"""
A module for implementing namespaces.
"""

# internal
from vcorelib.namespace.base import CPP_DELIM, DEFAULT_DELIM, Namespace
from vcorelib.namespace.mixin import NamespaceMixin

__all__ = ["DEFAULT_DELIM", "CPP_DELIM", "Namespace", "NamespaceMixin"]
