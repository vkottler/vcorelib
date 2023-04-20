"""
A module aggregating all data-arbiter capabilities.
"""

# internal
from vcorelib.io.arbiter.context import DataArbiterContext


class DataArbiter(DataArbiterContext):
    """A class aggregating all data-arbiter capabilities."""


ARBITER = DataArbiter()
