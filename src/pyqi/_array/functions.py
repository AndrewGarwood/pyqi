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
from ..validation import require
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


def partition(arr: Iterable[T], batch_size: int, /) -> list[tuple[T, ...]]:
    batch_size = require.positive_integer(batch_size)
    elements = tuple(x for x in arr)
    N = len(elements)
    if (not N): return []
    
    batches: list[tuple[T, ...]] = []
    for start in range(0, N, batch_size):
        batches.append(elements[start:min(start+batch_size, N)])
    
    return batches


def every(
    arr: Iterable[T], 
    fn: Callable[[T], bool]=bool, 
    /
) -> bool:
    """ *`@returns`* `all(map(arr, fn))` """
    return all(map(arr, fn))

def some(
    arr: Iterable[T], 
    fn: Callable[[T], bool]=bool, 
    /
) -> bool:
    """ *`@returns`* `any(map(arr, fn))` """
    return any(map(arr, fn))


def isArray(arr: Any) -> TypeGuard[list[Any] | tuple[Any,...]]:
    return isinstance(arr, (list, tuple))

def isNonAtomicSequence(arr: Any) -> TypeGuard[Sequence[Any]]:
    return (not is_atomic(arr) and (isinstance(arr, Sequence)))


__all__ = export(map, forEach, every, some, isArray, isNonAtomicSequence, partition)