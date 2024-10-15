"""
A module implementing a logger interface that uses lists.
"""

# built-in
import logging

# third-party
from vcorelib.logging.args import DEFAULT_TIME_FORMAT


class ListLogger(logging.Handler):
    """An interface facilitating sending log messages to browser tabs."""

    log_messages: list[logging.LogRecord]

    def drain(self) -> list[logging.LogRecord]:
        """Drain messages."""

        result = self.log_messages
        self.log_messages = []
        return result

    def drain_str(self) -> list[str]:
        """Drain formatted messages."""

        result = []
        for record in self.drain():
            result.append(
                self.format(record)
                # Respect 'external' logs that don't warrant full formatting.
                if not getattr(record, "external", False)
                else record.getMessage()
            )
        return result

    def __bool__(self) -> bool:
        """Evaluate this instance as boolean."""
        return bool(self.log_messages)

    def emit(self, record: logging.LogRecord) -> None:
        """Send the log message."""

        self.log_messages.append(record)

    @staticmethod
    def create(fmt: str = DEFAULT_TIME_FORMAT) -> "ListLogger":
        """Create an instance of this handler."""

        logger = ListLogger()
        logger.log_messages = []
        logger.setFormatter(logging.Formatter(fmt))
        return logger
