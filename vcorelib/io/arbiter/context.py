"""
A module implementing various context-manager interfaces for the data arbiter.
"""

# built-in
from contextlib import asynccontextmanager as _asynccontextmanager
from contextlib import contextmanager as _contextmanager
from typing import AsyncIterator as _AsyncIterator
from typing import Iterator as _Iterator

# internal
from vcorelib.dict import GenericStrDict as _GenericStrDict
from vcorelib.io.arbiter.directory import DataArbiterDirectories
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize


class DataArbiterContext(DataArbiterDirectories):
    """A class implementing context-manager interfaces for the data arbiter."""

    @_asynccontextmanager
    async def object_file_context_async(
        self,
        pathlike: _Pathlike,
        decode_kwargs: _GenericStrDict = None,
        encode_kwargs: _GenericStrDict = None,
    ) -> _AsyncIterator[_JsonObject]:
        """
        Provide data loaded from a file as a context so that it's written back
        when the context ends.
        """
        if decode_kwargs is None:
            decode_kwargs = {}
        if encode_kwargs is None:
            encode_kwargs = {}

        path = normalize(pathlike)

        data = (await self.decode_async(path, **decode_kwargs)).data
        yield data
        assert (await self.encode_async(path, data, **encode_kwargs))[
            0
        ], f"Encoding '{path}' as a file failed!"

    @_contextmanager
    def object_file_context(
        self,
        pathlike: _Pathlike,
        decode_kwargs: _GenericStrDict = None,
        encode_kwargs: _GenericStrDict = None,
    ) -> _Iterator[_JsonObject]:
        """
        Provide data loaded from a file as a context so that it's written back
        when the context ends.
        """
        if decode_kwargs is None:
            decode_kwargs = {}
        if encode_kwargs is None:
            encode_kwargs = {}

        path = normalize(pathlike)

        data = self.decode(path, **decode_kwargs).data
        yield data
        assert self.encode(path, data, **encode_kwargs)[
            0
        ], f"Encoding '{path}' as a file failed!"

    @_contextmanager
    def object_directory_context(
        self,
        pathlike: _Pathlike,
        decode_kwargs: _GenericStrDict = None,
        encode_kwargs: _GenericStrDict = None,
    ) -> _Iterator[_JsonObject]:
        """Provide a loaded directory as a context."""

        if decode_kwargs is None:
            decode_kwargs = {}
        if encode_kwargs is None:
            encode_kwargs = {}

        # Make sure the directory exists, since we would create it anyway.
        path = normalize(pathlike)
        path.mkdir(parents=True, exist_ok=True)

        data = self.decode_directory(path, **decode_kwargs).data
        yield data
        assert self.encode_directory(
            path,
            data,
            **encode_kwargs,
        )[0], f"Encoding '{path}' as a directory failed!"

    @_asynccontextmanager
    async def object_directory_context_async(
        self,
        pathlike: _Pathlike,
        decode_kwargs: _GenericStrDict = None,
        encode_kwargs: _GenericStrDict = None,
    ) -> _AsyncIterator[_JsonObject]:
        """Provide a loaded directory as a context."""

        if decode_kwargs is None:
            decode_kwargs = {}
        if encode_kwargs is None:
            encode_kwargs = {}

        # Make sure the directory exists, since we would create it anyway.
        path = normalize(pathlike)
        path.mkdir(parents=True, exist_ok=True)

        data = (await self.decode_directory_async(path, **decode_kwargs)).data
        yield data
        assert (
            await self.encode_directory_async(
                path,
                data,
                **encode_kwargs,
            )
        )[0], f"Encoding '{path}' as a directory failed!"
