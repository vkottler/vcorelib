"""
vcorelib - Dictionary manipulation utilities.
"""

# built-in
from logging import Logger, getLogger
from typing import List

LOG = getLogger(__name__)


def merge(
    dict_a: dict,
    dict_b: dict,
    path: List[str] = None,
    expect_overwrite: bool = False,
    logger: Logger = LOG,
) -> dict:
    """
    Combine two dictionaries recursively, prefers dict_a in a conflict. For
    values of the same key that are lists, the lists are combined. Otherwise
    the resulting dictionary is cleanly merged.
    """

    if path is None:
        path = []

    for key, right_val in dict_b.items():
        if key in dict_a:
            # first try to coerce b's type into a's
            if not isinstance(right_val, type(dict_a[key])):
                try:
                    right_val = type(dict_a[key])(right_val)
                except ValueError:
                    pass

            # same leaf value
            if dict_a[key] == right_val:
                pass
            elif isinstance(dict_a[key], dict) and isinstance(right_val, dict):
                merge(
                    dict_a[key],
                    right_val,
                    path + [str(key)],
                    expect_overwrite,
                    logger,
                )
            elif isinstance(dict_a[key], list) and isinstance(right_val, list):
                dict_a[key].extend(right_val)
            elif not isinstance(right_val, type(dict_a[key])):
                logger.error(
                    "Type mismatch at '%s'", ".".join(path + [str(key)])
                )
                logger.error("left:  %s (%s)", type(dict_a[key]), dict_a[key])
                logger.error("right: %s (%s)", type(right_val), right_val)
            elif not expect_overwrite:
                logger.error("Conflict at '%s'", ".".join(path + [str(key)]))
                logger.error("left:  %s", dict_a[key])
                logger.error("right: %s", right_val)
            else:
                dict_a[key] = right_val
        else:
            dict_a[key] = right_val

    return dict_a


def merge_dicts(
    dicts: List[dict],
    expect_overwrite: bool = False,
    logger: Logger = LOG,
) -> dict:
    """
    Merge a list of dictionary data into a single set (mutates the first
    element).
    """

    result = dicts[0]
    for right_dict in dicts[1:]:
        result = merge(
            result,
            right_dict,
            expect_overwrite=expect_overwrite,
            logger=logger,
        )
    return result
