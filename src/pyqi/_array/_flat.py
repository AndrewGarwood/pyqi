"""
*`@file`* `_array/_flat`
"""
from __future__ import annotations
from itertools import chain
from collections.abc import (Iterable)
from typing import (
    Any, TypeVar,
)
from ..types import (is_atomic)
from ..utils.module import export

T = TypeVar('T')
U = TypeVar('U')

def flat1(arr: Iterable[Iterable[T]], /) -> list[T]:
    """ *`@returns`* `list(chain.from_iterable(arr))` """
    return list(chain.from_iterable(arr))

def flat(
    arr: Iterable[Any], 
    /,
    depth: int = 1, 
):
    if depth <= 0:
        return list(arr)
    result = []
    for item in arr:
        if depth > 0 and can_flatten(item):
            result.extend(flat(item, depth-1))
        else:
            result.append(item)
    return result

def flatten_all(arr: Iterable[Any], /): #  -> list[Any]
    result: list[Any] = []
    for item in arr:
        if can_flatten(item):
            result.extend(flatten_all(item))
        else:
            result.append(item)
    return result


def can_flatten(value: object, /) -> bool:
    return (
        isinstance(value, Iterable) 
        and not is_atomic(value)
    )

__all__ = export(flat, flat1, flatten_all, can_flatten)