"""
*`@file`* `_array/_filter`
"""
from __future__ import annotations
from itertools import chain
from collections.abc import (Iterable, Iterator)
from typing import (
    Any, Callable, Literal,  Optional, Sequence, 
    TypeVar, overload, TypeGuard
)
from ..utils.module import export

T = TypeVar('T')
U = TypeVar('U')

@overload
def filter(arr: Iterable[T | None], fn: None, /) -> list[T]: ...

@overload
def filter(arr: Iterable[T], fn: Callable[[T], TypeGuard[U]], /) -> list[U]: ...

@overload
def filter(arr: Iterable[T], fn: Callable[[T], bool], /) -> list[T]: ...

def filter(arr: Iterable[T], fn: Callable[[T], Any] | None, /) -> list[Any]:
    """ *`@returns`* `[x for x in arr if fn(x)]` """
    if (fn is None):
        return [x for x in arr if x is not None]
    return [x for x in arr if fn(x)]


def filter_map(arr: Iterable[T], fn: Callable[[T], U | None],/) -> list[U]:
    """ 
    *`@returns`* `[x for x in (fn(y) for y in arr) if x is not None]`
    - i.e. `fn(y) for y in arr if fn(y) is not None`
    - i.e. filter out `None` from map `fn`
    """
    return [x for x in (fn(y) for y in arr) if x is not None]

__all__ = export(filter, filter_map)