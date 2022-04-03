"""
Utilities for working with environment-variable data contained inside various
data structures.
"""

# built-in
from os import environ as _environ
from typing import List as _List


def str_resolve_env_var(data: str) -> str:
    """
    Convert string data to a resolved environment variable if the string begins
    with '$' and is a key in the environment with a non-empty value.
    """

    temp = data.strip()
    if temp.startswith("$"):
        key = temp[1:]
        if key in _environ and _environ[key]:
            data = _environ[key]

    return data


def list_resolve_env_vars(
    data: list, keys: bool = True, values: bool = True, lists: bool = True
) -> list:
    """
    Recursively resolve list data that may contain strings that should be
    treated as environment-variable substitutions. The data is updated
    in-place.
    """

    for idx, item in enumerate(data):
        if isinstance(item, dict) and (keys or values):
            data[idx] = dict_resolve_env_vars(item, keys, values, lists)
        if isinstance(item, list) and lists:
            data[idx] = list_resolve_env_vars(item, keys, values, lists)
        if isinstance(item, str):
            data[idx] = str_resolve_env_var(item)

    return data


def dict_resolve_env_vars(
    data: dict, keys: bool = True, values: bool = True, lists: bool = True
) -> dict:
    """
    Recursively resolve dictionary data that may contain strings that should be
    treated as environment-variable substitutions. The data is updated
    in-place.
    """

    keys_to_remove: _List[str] = []
    to_update: dict = {}
    for key, value in data.items():

        if isinstance(value, str) and values:
            value = str_resolve_env_var(value)

        if isinstance(key, str) and keys:
            to_update[str_resolve_env_var(key)] = value
            keys_to_remove.append(key)

        data[key] = value

        if isinstance(value, dict):
            data[key] = dict_resolve_env_vars(value, keys, values, lists)
        if isinstance(value, list) and lists:
            data[key] = list_resolve_env_vars(value, keys, values, lists)

    # Don't change the size of data while iterating.
    for key in keys_to_remove:
        del data[key]
    data.update(to_update)

    return data
