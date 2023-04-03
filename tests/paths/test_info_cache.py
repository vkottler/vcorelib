"""
Tests for the 'paths.info_cache' module.
"""

# built-in
from contextlib import ExitStack
from logging import getLogger
from os import linesep
from pathlib import Path
from tempfile import TemporaryDirectory

# module under test
from vcorelib.paths.context import tempfile
from vcorelib.paths.info_cache import (
    FileChanged,
    FileInfo,
    FileInfoManager,
    file_info_cache,
)

LOG = getLogger(__name__)


def test_paths_file_info_cache():  # pylint: disable=too-many-locals
    """Test that file info caching works."""

    last_result = False

    def fresh_callback(change: FileChanged) -> bool:
        """Sample callback."""

        del change

        nonlocal last_result
        last_result = not last_result
        return last_result

    with ExitStack() as stack:
        cache_locs = [
            stack.enter_context(tempfile(suffix=".json")),
            stack.enter_context(tempfile(suffix=".json")),
        ]

        for cache_loc in cache_locs:
            tmpdir = Path(stack.enter_context(TemporaryDirectory()))

            subdir = tmpdir.joinpath("tmp")
            subdir.mkdir()
            tdirs = [tmpdir, subdir]

            files = [tmpdir.joinpath(f"{idx}.txt") for idx in range(10)]
            files += [subdir.joinpath(f"sub{idx}.txt") for idx in range(10)]

            with file_info_cache(
                cache_loc, fresh_callback, logger=LOG
            ) as manager:
                for directory in tdirs:
                    manager.poll_directory(
                        directory, recurse=True, base=tmpdir
                    )

                for file in files:
                    with file.open("w", encoding="utf-8") as path_fd:
                        path_fd.write("test1" + linesep)
                        path_fd.flush()

                finfo = FileInfo.from_file(files[0])
                assert finfo == FileInfo.from_file(files[0])
                assert hash(finfo)
                assert finfo.to_json()
                finfo.poll()

                for directory in tdirs:
                    manager.poll_directory(
                        directory, recurse=True, base=tmpdir
                    )

                for file in files:
                    file.unlink()

                manager.poll_existing(base=tmpdir)

                for file in files:
                    with file.open("w", encoding="utf-8") as path_fd:
                        path_fd.write("test 2" + linesep)
                        path_fd.flush()

                for directory in tdirs:
                    manager.poll_directory(
                        directory, recurse=True, base=tmpdir
                    )

                with file_info_cache(
                    cache_loc, fresh_callback, logger=LOG
                ) as _:
                    pass

                for file in files:
                    file.unlink()
                finfo.poll()

                for directory in tdirs:
                    manager.poll_directory(directory, True, base=tmpdir)

            # Load the file info.
            new_manager = FileInfoManager(fresh_callback)
            new_manager = FileInfoManager(fresh_callback, manager.infos)
            for directory in tdirs:
                new_manager.poll_directory(directory, True, base=tmpdir)

            for file in files:
                with file.open("w", encoding="utf-8") as path_fd:
                    path_fd.write("test3" + linesep)
                    path_fd.flush()

            with file_info_cache(
                cache_loc, fresh_callback, logger=LOG
            ) as manager:
                assert manager.infos
