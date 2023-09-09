"""
A module implementing a JSON message processor interface.
"""

# built-in
import asyncio
from copy import copy
from json import dumps
import logging
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, Union

# internal
from vcorelib import PKG_NAME, VERSION
from vcorelib.dict.codec import JsonCodec
from vcorelib.logging import LoggerMixin
from vcorelib.target.resolver import TargetResolver
from vcorelib.task.json.handlers import (
    FindFile,
    event_wait,
    find_file_request_handler,
    loopback_handler,
)

# RESERVED_KEYS,
from vcorelib.task.json.types import (
    DEFAULT_LOOPBACK,
    DEFAULT_TIMEOUT,
    JsonMessage,
    MessageHandler,
    T,
    TypedHandler,
)


class JsonMessageProcessor(LoggerMixin):
    """A simple JSON message sending and receiving interface."""

    package = PKG_NAME
    version = VERSION

    def __init__(self) -> None:
        """Initialize this instance."""

        super().__init__()

        self.targets = TargetResolver()

        self.curr_id: int = 1

        self.ids_waiting: Dict[int, asyncio.Event] = {}
        self.id_responses: Dict[int, JsonMessage] = {}

        self._log_messages: List[Dict[str, Any]] = []
        self.remote_meta: Optional[JsonMessage] = None

        # Standard handlers.
        self.basic_handler("loopback")
        self.basic_handler("meta", self._meta_handler)

        self._register_handlers()

        self.meta(log=True)

    def _register_handlers(self) -> None:
        """Register connection-specific command handlers."""

        # Extra handlers.
        self.typed_handler("find_file", FindFile, find_file_request_handler)

    def meta(self, log: bool = False) -> JsonMessage:
        """Get metadata for this message processor."""

        result = {
            "package": self.package,
            "version": self.version,
            "kind": type(self).__name__,
            "handlers": list(self.handlers()),
        }

        if log:
            self.logger.info(
                "metadata: package=%s, version=%s, kind=%s, handlers=%s",
                result["package"],
                result["version"],
                result["kind"],
                result["handlers"],
            )

        return result

    def handlers(self) -> Iterator[str]:
        """Iterate over all available key handlers."""

        yield from self.targets.literals
        for target in self.targets.dynamic:
            yield target.data

    def basic_handler(
        self, key: str, handler: MessageHandler = loopback_handler
    ) -> None:
        """Register a basic handler."""

        assert self.targets.register(key, (key, handler, None))

    def typed_handler(
        self, key: str, kind: Type[T], handler: TypedHandler[T]
    ) -> None:
        """Register a typed handler."""

        assert self.targets.register(key, (key, handler, kind))

    def stage_remote_log(
        self, msg: str, *args, level: int = logging.INFO
    ) -> None:
        """Log a message on the remote."""

        data = {"msg": msg, "level": level}
        if args:
            data["args"] = [*args]
        self._log_messages.append(data)

    def send_message_str(
        self, data: str, addr: Tuple[str, int] = None
    ) -> None:
        """TODO."""

    def send_json(
        self, data: Union[JsonMessage, JsonCodec], addr: Tuple[str, int] = None
    ) -> None:
        """Send a JSON message."""

        if isinstance(data, JsonCodec):
            data = data.asdict()

        # Add any pending log messages to this message.
        if self._log_messages:
            assert "__log_messages__" not in data
            data["__log_messages__"] = self._log_messages  # type: ignore
            self._log_messages = []

        self.send_message_str(dumps(data, separators=(",", ":")), addr=addr)

    async def wait_json(
        self,
        data: Union[JsonMessage, JsonCodec],
        addr: Tuple[str, int] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> JsonMessage:
        """Send a JSON message and wait for a response."""

        if isinstance(data, JsonCodec):
            data = data.asdict()

        data = copy(data)
        assert "__id__" not in data, data
        data["__id__"] = self.curr_id

        got_response = asyncio.Event()

        ident = self.curr_id
        self.curr_id += 1

        assert ident not in self.ids_waiting
        self.ids_waiting[ident] = got_response

        # Send message and await response.
        self.send_json(data, addr=addr)

        assert await event_wait(
            got_response, timeout
        ), f"No response received in {timeout} seconds!"

        # Return the result.
        result = self.id_responses[ident]
        del self.id_responses[ident]

        return result

    async def loopback(
        self,
        data: JsonMessage = None,
        addr: Tuple[str, int] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> bool:
        """Perform a simple loopback test on this connection."""

        if data is None:
            data = DEFAULT_LOOPBACK

        message = {"loopback": data}
        response = await self.wait_json(message, addr=addr, timeout=timeout)
        status = response == message

        self.logger.info(
            "Loopback result: '%s' (%s).",
            response,
            "success" if status else "fail",
        )

        return status

    async def _meta_handler(
        self, outbox: JsonMessage, inbox: JsonMessage
    ) -> None:
        """Handle the peer's metadata."""

        if self.remote_meta is None:
            self.remote_meta = inbox
            outbox.update(self.meta())

            # Log peer's metadata.
            self.logger.info(
                (
                    "remote metadata: package=%s, "
                    "version=%s, kind=%s, handlers=%s"
                ),
                self.remote_meta["package"],
                self.remote_meta["version"],
                self.remote_meta["kind"],
                self.remote_meta["handlers"],
            )

    def _handle_reserved(
        self, data: JsonMessage, response: JsonMessage
    ) -> bool:
        """Handle special keys in an incoming message."""

        should_respond = True

        # If a message identifier is present, send one in the response.
        if "__id__" in data:
            ident = data["__id__"]
            if ident in self.ids_waiting:
                del data["__id__"]
                self.id_responses[ident] = data
                event = self.ids_waiting[ident]
                del self.ids_waiting[ident]
                event.set()

                # Don't respond if we're receiving a reply.
                should_respond = False

            response["__id__"] = ident

        # Log messages sent by the peer.
        if "__log_messages__" in data:
            for message in data["__log_messages__"]:
                if "msg" in message and message["msg"]:
                    self.logger.log(
                        message.get("level", logging.INFO),
                        "remote: " + message["msg"],
                        *message.get("args", []),
                    )

        return should_respond
