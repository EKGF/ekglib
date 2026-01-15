#
# Copied from:
# https://codereview.stackexchange.com/questions/145757/finding-a-common-prefix-suffix-in-a-list-tuple-of-strings
#
from itertools import zip_longest
from typing import Any, Union

from ekg_lib.exceptions.exceptions import PrefixException


def all_same(items: Union[tuple[Any, ...], list[Any], str]) -> bool:
    """
    A helper function to test if
    all items in the given iterable
    are identical.

    Arguments:
    item -> the given iterable to be used

    eg.
    >>> all_same([1, 1, 1])
    True
    >>> all_same([1, 1, 2])
    False
    >>> all_same((1, 1, 1))
    True
    >> all_same((1, 1, 2))
    False
    >>> all_same("111")
    True
    >>> all_same("112")
    False
    """
    return all(item == items[0] for item in items)


def common_prefix(
    strings: Union[list[str], tuple[str, ...]], _min: int = 0, _max: int = 100
) -> str:
    """
    Given a list or tuple of strings, find the common prefix_
    among them. If a common prefix_ is not found, an empty string
    will be returned.

    Arguments:
    strings -> the string list or tuple to
    be used.

    _min, _max - > If a common prefix_ is  found,
    Its length will be tested against the range _min
    and _max. If its length is not in the range, and
    empty string will be returned, otherwise the prefix_
    is returned

    eg.
    >>> common_prefix(['hello', 'hemp', 'he'])
    'he'
    >>> common_prefix(('foobar', 'foobaz', 'foobam'))
    'foo'
    >>> common_prefix(['foobar', 'foobaz', 'doobam'])
    ''
    """
    prefix = ''
    for tup in zip_longest(*strings):
        if all_same(tup):
            prefix += tup[0]
        else:
            if _min <= len(prefix) <= _max:
                return prefix
            else:
                return ''
    if _min <= len(prefix) <= _max:
        return prefix
    else:
        return ''


def common_suffix(
    strings: Union[list[str], tuple[str, ...]], _min: int = 0, _max: int = 100
) -> str:
    """
    Given a list or tuple of strings, find the common suffix
    among them. If a common suffix is not found, an empty string
    will be returned.

    Arguments:
    strings -> the string list or tuple to
    be used.

    _min, _max - > If a common suffix is  found,
    Its length will be tested against the range _min
    and _max. If its length is not in the range, and
    empty string will be returned, otherwise the suffix
    is returned

    eg.
    >>> common_suffix(['rhyme', 'time', 'mime'])
    'me'
    >>> common_suffix(('boo', 'foo', 'goo'))
    'oo'
    >>> common_suffix(['boo', 'foo', 'goz'])
    ''
    """
    suffix = ''
    strings = [string[::-1] for string in strings]
    for tup in zip_longest(*strings):
        if all_same(tup):
            suffix += tup[0]
        else:
            if _min <= len(suffix) <= _max:
                return suffix[::-1]
            else:
                return ''
    if _min <= len(suffix) <= _max:
        return suffix[::-1]
    else:
        return ''


def remove_prefix(text: str, prefix_: str) -> str:
    if text.startswith(prefix_):
        text = text.strip()
        if len(prefix_) == len(text):
            raise PrefixException(
                f"Cannot remove prefix '{prefix_}' from string '{text}'"
            )
        return text[len(prefix_) :]
    return text


def strip_end(text: str, suffix: str) -> str:
    text = text.strip()
    if not text.endswith(suffix):
        return text
    return text[: len(text) - len(suffix)]
