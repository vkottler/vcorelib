"""
A data-arbiter extension for working with directories.
"""

# built-in
from pathlib import Path
from typing import Callable as _Callable
from typing import cast as _cast

# internal
from vcorelib.dict import MergeStrategy, merge
from vcorelib.io.arbiter.base import DataArbiterBase
from vcorelib.io.types import DEFAULT_DATA_EXT as _DEFAULT_DATA_EXT
from vcorelib.io.types import EncodeResult as _EncodeResult
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue
from vcorelib.io.types import LoadResult
from vcorelib.logging import LoggerType
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import get_file_name, normalize


class DataArbiterDirectories(DataArbiterBase):
    """A class adding interfaces for working with directories."""

    def encode_directory(
        self,
        pathlike: _Pathlike,
        data: _JsonObject,
        ext: str = _DEFAULT_DATA_EXT,
        logger: LoggerType = None,
        **kwargs,
    ) -> _EncodeResult:
        """
        Encode data to a directory where every key becomes a file with the
        provided extension. The encoding scheme is implied by the extension.
        """

        success = True
        time_ns = 0
        root = normalize(pathlike)

        for key, item in data.items():
            result = self.encode(
                root.joinpath(f"{key}.{ext}"),
                _cast(_JsonObject, item),
                logger,
                **kwargs,
            )
            success &= result[0]
            if result[1]:
                time_ns += result[1]

        return success, time_ns

    def decode_directory(
        self,
        pathlike: _Pathlike,
        logger: LoggerType = None,
        require_success: bool = False,
        path_filter: _Callable[[Path], bool] = None,
        recurse: bool = False,
        **kwargs,
    ) -> LoadResult:
        """
        Attempt to decode data files in a directory. Assigns data loaded from
        each file to a key, returns whether or not any files failed to load
        and the cumulative time that each file-load took.
        """

        data: _JsonObject = {}
        path = normalize(pathlike)
        errors = 0
        load_time = 0

        for child in filter(
            path_filter if path_filter is not None else lambda _: True,
            path.iterdir(),
        ):
            load = None
            if child.is_file():
                load = self.decode(
                    child,
                    logger=logger,
                    require_success=require_success,
                    **kwargs,
                )
            elif recurse and child.is_dir():
                load = self.decode_directory(
                    child,
                    logger=logger,
                    require_success=require_success,
                    path_filter=path_filter,
                    recurse=recurse,
                    **kwargs,
                )

            if load is not None:
                if load.success:
                    key = get_file_name(child)
                    if key:
                        data[key] = _cast(_JsonValue, load.data)
                    else:
                        data = merge(
                            data,
                            load.data,
                            expect_overwrite=kwargs.get(
                                "expect_overwrite", False
                            ),
                            strategy=kwargs.get(
                                "strategy", MergeStrategy.RECURSIVE
                            ),
                            logger=logger,
                        )
                errors += int(not load.success)
                if load.time_ns:
                    load_time += load.time_ns

        return LoadResult(data, errors == 0, load_time)
