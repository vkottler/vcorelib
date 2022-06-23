"""
A module for extracting and creating arbitrary archives.
"""

# built-in
from os import chdir as _chdir
from os import getcwd as _getcwd
from pathlib import Path
import shutil
import tarfile
from typing import Optional as _Optional
from typing import Tuple as _Tuple
import zipfile

# internal
from vcorelib.io.types import DEFAULT_ARCHIVE_EXT as _DEFAULT_ARCHIVE_EXT
from vcorelib.io.types import FileExtension
from vcorelib.math.time import TIMER as _TIMER


def extractall(
    src: Path, dst: Path = None, maxsplit: int = 1, **extract_kwargs
) -> _Tuple[bool, int]:
    """
    Attempt to extract an arbitrary archive to a destination. Return whether or
    not this succeeded and how long it took.
    """

    success = False
    time_ns = -1
    ext = FileExtension.from_path(src, maxsplit=maxsplit)

    # Ensure that the source directory is an archive.
    if ext is None or not ext.is_archive() or not src.is_file():
        return success, time_ns

    if dst is None:
        dst = Path()

    with _TIMER.measure_ns() as token:

        # Extract the tar archive.
        if ext is FileExtension.TAR:
            with tarfile.open(src) as tar:
                tar.extractall(dst, **extract_kwargs)
            success = True

        # Extract the ZIP archive.
        elif ext is FileExtension.ZIP:
            with zipfile.ZipFile(src) as zipf:
                zipf.extractall(dst, **extract_kwargs)
            success = True

    return success, _TIMER.result(token)


def make_archive(
    src_dir: Path,
    ext_str: str = _DEFAULT_ARCHIVE_EXT,
    dst_dir: Path = None,
    **archive_kwargs,
) -> _Tuple[_Optional[Path], int]:
    """
    Create an archive from a source directory, named after that directory,
    and optionally moved to a destination other than the parent directory
    for the source. The extension specifies the kind of archive to create.

    Return the path to the created archive (if it was created) and how long
    it took to create.
    """

    result = None
    time_ns = -1

    if not src_dir.is_dir():
        return result, time_ns

    # Map file extensions to the archiver's known formats. Some extensions
    # don't require any mapping (e.g. "tar", "zip").
    format_map = {
        "tar.gz": "gztar",
        "tar.bz2": "bztar",
        "tar.lzma": "xztar",
        "tar.xz": "xztar",
    }
    format_str = format_map.get(ext_str, ext_str)

    # Make sure that this output format is supported.
    if format_str not in [x[0] for x in shutil.get_archive_formats()]:
        return result, time_ns

    curr = _getcwd()
    try:
        _chdir(src_dir.parent)

        with _TIMER.measure_ns() as token:
            result = Path(
                shutil.make_archive(
                    src_dir.name,
                    format_str,
                    base_dir=src_dir.name,
                    **archive_kwargs,
                )
            ).resolve()
        time_ns = _TIMER.result(token)

        # Move the resulting archive, if requested.
        if dst_dir is not None:
            dst_dir.mkdir(parents=True, exist_ok=True)
            new_path = Path(dst_dir, result.name)
            assert not new_path.is_dir()
            shutil.move(str(result), new_path)
            result = new_path
    finally:
        _chdir(curr)

    return result, time_ns
