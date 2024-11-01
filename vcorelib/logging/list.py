"""
A module implementing a logger interface that uses lists.
"""

# built-in
import logging
from typing import Iterator

# third-party
from vcorelib.logging.args import DEFAULT_TIME_FORMAT


class ListLogger(logging.Handler):
    """An interface facilitating sending log messages to browser tabs."""

    max_size: int = 2**10
    dropped: int

    log_messages: list[logging.LogRecord]

    def drain(self) -> list[logging.LogRecord]:
        """Drain messages."""

        result = self.log_messages
        self.log_messages = []
        return result

    def drain_str_iter(self) -> Iterator[str]:
        """Iterate over string messages."""

        for record in self.drain():
            yield (
                self.format(record)
                # Respect 'external' logs that don't warrant full formatting.
                if not getattr(record, "external", False)
                else record.getMessage()
            )

        # Create a message for drops.
        if self.dropped:
            yield (
                f"(logger dropped {self.dropped} messages, "
                f"max_size={self.max_size})"
            )
            self.dropped = 0

    def drain_str(self) -> list[str]:
        """Drain formatted messages."""
        return list(self.drain_str_iter())

    def __bool__(self) -> bool:
        """Evaluate this instance as boolean."""
        return bool(self.log_messages)

    def emit(self, record: logging.LogRecord) -> None:
        """Send the log message."""

        # Could do something with the lost messages at some point.
        while len(self.log_messages) >= self.max_size:
            self.log_messages.pop(0)
            self.dropped += 1

        self.log_messages.append(record)

    @staticmethod
    def create(fmt: str = DEFAULT_TIME_FORMAT) -> "ListLogger":
        """Create an instance of this handler."""

        logger = ListLogger()
        logger.log_messages = []
        logger.dropped = 0
        logger.setFormatter(logging.Formatter(fmt))
        return logger
