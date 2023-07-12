"""
A module for hashing file data.
"""

# built-in
from hashlib import md5 as _md5
from hashlib import new as _new
from os import linesep as _linesep
from pathlib import Path as _Path

# internal
from vcorelib import DEFAULT_ENCODING as _DEFAULT_ENCODING
from vcorelib.paths.base import Pathlike, normalize

DEFAULT_HASH = "sha256"


def create_hex_digest(
    output: Pathlike,
    name: str,
    sources: Pathlike = None,
    algorithm: str = DEFAULT_HASH,
) -> _Path:
    """Create a hex digest file based on file hashes in some directory."""

    output = normalize(output)

    # Use the output directory as the directory to iterate over sources if
    # one wasn't provided.
    if sources is None:
        sources = output
    sources = normalize(output)
    assert sources.is_dir(), f"'{sources}' is not a directory!"

    # Determine files to has before we create an additional file.
    to_hash = [x for x in sources.iterdir() if x.is_file()]

    hex_digest = output.joinpath(f"{name}.{algorithm}sum")
    with hex_digest.open("w", encoding=_DEFAULT_ENCODING) as sha_fd:
        for item in to_hash:
            sha_fd.write(file_hash_hex(item, algorithm=algorithm))
            sha_fd.write(" *")
            sha_fd.write(item.name)
            sha_fd.write(_linesep)

    return hex_digest


def bytes_hash_hex(data: bytes, algorithm: str = DEFAULT_HASH) -> str:
    """
    Get the hex digest from some bytes for some provided hashing algorithm.
    """
    inst = _new(algorithm)
    inst.update(data)
    return inst.hexdigest()


def str_hash_hex(
    data: str, encoding: str = _DEFAULT_ENCODING, algorithm: str = DEFAULT_HASH
) -> str:
    """Get the hex digest for string data."""
    return bytes_hash_hex(bytes(data, encoding), algorithm=algorithm)


def file_hash_hex(path: Pathlike, algorithm: str = DEFAULT_HASH) -> str:
    """Get the hex digest from file data."""
    with normalize(path).open("rb") as stream:
        return bytes_hash_hex(stream.read(), algorithm=algorithm)


def bytes_md5_hex(data: bytes) -> str:
    """Get the MD5 sum for some bytes."""
    return _md5(data).hexdigest()


def str_md5_hex(data: str, encoding: str = _DEFAULT_ENCODING) -> str:
    """Get an md5 hex string from string data."""
    return bytes_md5_hex(bytes(data, encoding))


def file_md5_hex(path: Pathlike) -> str:
    """Get an md5 hex string for a file by path."""
    with normalize(path).open("rb") as stream:
        return bytes_md5_hex(stream.read())
