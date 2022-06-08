"""
Tests for the 'paths.info_cache' module.
"""

from contextlib import ExitStack

# built-in
from os import linesep
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Optional

# module under test
from vcorelib.paths.info_cache import (
    FileInfo,
    FileInfoManager,
    file_info_cache,
)


def test_paths_file_info_cache():  # pylint: disable=too-many-locals
    """Test that file info caching works."""

    def fresh_callback(
        new: Optional[FileInfo], curr: Optional[FileInfo]
    ) -> None:
        """Sample callback."""
        del new
        del curr

    with NamedTemporaryFile(suffix=".json") as tfile:
        name = tfile.name

    cache_locs = [Path(name)]

    with ExitStack() as stack:
        cache_locs.append(Path(stack.enter_context(TemporaryDirectory())))
        for cache_loc in cache_locs:

            tmpdir = Path(stack.enter_context(TemporaryDirectory()))
            subdir = tmpdir.joinpath("tmp")
            subdir.mkdir()
            tdirs = [tmpdir, subdir]

            files = [tmpdir.joinpath(f"{idx}.txt") for idx in range(10)]
            files += [subdir.joinpath(f"sub{idx}.txt") for idx in range(10)]

            with file_info_cache(cache_loc, fresh_callback) as manager:

                for directory in tdirs:
                    manager.poll_directory(directory, True)

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
                    manager.poll_directory(directory, True)

                for file in files:
                    with file.open("w", encoding="utf-8") as path_fd:
                        path_fd.write("test2" + linesep)
                        path_fd.flush()

                for directory in tdirs:
                    manager.poll_directory(directory, True)

                with file_info_cache(cache_loc, fresh_callback) as _:
                    pass

                for file in files:
                    file.unlink()
                finfo.poll()

                for directory in tdirs:
                    manager.poll_directory(directory, True)

            # Load the file info.
            new_manager = FileInfoManager(fresh_callback)
            new_manager = FileInfoManager(fresh_callback, manager.infos)
            for directory in tdirs:
                new_manager.poll_directory(directory, True)

            for file in files:
                with file.open("w", encoding="utf-8") as path_fd:
                    path_fd.write("test3" + linesep)
                    path_fd.flush()

            with file_info_cache(cache_loc, fresh_callback) as manager:
                pass
