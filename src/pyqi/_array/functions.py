"""
*`@file`* `_array/functions.py`
"""
from __future__ import annotations
from collections.abc import (Iterable)
from typing import (
    Any, Callable, Sequence, 
    TypeVar, TypeGuard
)
from ..utils.module import export
from ..types import (is_atomic)

T = TypeVar('T')
U = TypeVar('U')

def map(arr: Iterable[T], fn: Callable[[T], U], /) -> list[U]:
    """ *`@returns`* `[fn(x) for x in arr]` """
    return [fn(x) for x in arr]


def forEach(arr: Iterable[T], fn: Callable[[T], U], /) -> None:
    """ `for x in arr: fn(x)` """
    for x in arr: fn(x)
    return None

def every(arr: Iterable[T], fn: Callable[[T], bool]=lambda x: bool(x), /) -> bool:
    """ *`@returns`* `all(map(arr, fn))` """
    return all(map(arr, fn))

def some(arr: Iterable[T], fn: Callable[[T], bool]=lambda x: bool(x), /) -> bool:
    """ *`@returns`* `any(map(arr, fn))` """
    return any(map(arr, fn))


def isArray(arr: Any) -> TypeGuard[list[Any] | tuple[Any,...]]:
    return isinstance(arr, (list, tuple))

def isNonAtomicSequence(arr: Any) -> TypeGuard[Sequence[Any]]:
    return (not is_atomic(arr) and (isinstance(arr, Sequence)))

__all__ = export(map, forEach, every, some, isArray, isNonAtomicSequence)