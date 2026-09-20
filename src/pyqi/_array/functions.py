"""
*`@file`* `_array/functions.py`
"""

from __future__ import annotations
from itertools import chain
from collections.abc import (Iterable, Iterator)
from typing import (Any, Callable, Literal,  Optional, Sequence, TypeAlias, TypeVar, overload, TypeGuard)
from lute import LogMsg
import lute

T = TypeVar('T')
U = TypeVar('U')
Atomic: TypeAlias = str | bytes | bytearray

def _is_atomic(value: Any, /) -> TypeGuard[Atomic]:
    return isinstance(value, (str, bytes, bytearray))

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
        if depth > 0 and _can_flatten(item):
            result.extend(flat(item, depth-1))
        else:
            result.append(item)
    return result

def flatten_all(arr: Iterable[Any], /): #  -> list[Any]
    result: list[Any] = []
    for item in arr:
        if _can_flatten(item):
            result.extend(flatten_all(item))
        else:
            result.append(item)
    return result


def _can_flatten(value: object, /) -> bool:
    return (
        isinstance(value, Iterable) 
        and not _is_atomic(value)
    )

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


def map(arr: Iterable[T], fn: Callable[[T], U], /) -> list[U]:
    """ *`@returns`* `[fn(x) for x in arr]` """
    return [fn(x) for x in arr]

def filter_map(arr: Iterable[T], fn: Callable[[T], U | None],/) -> list[U]:
    """ 
    *`@returns`* `[x for x in (fn(y) for y in arr) if x is not None]`
    - i.e. `fn(y) for y in arr if fn(y) is not None`
    - i.e. filter out `None` from map `fn`
    """
    return [x for x in (fn(y) for y in arr) if x is not None]


def forEach(arr: Iterable[T], fn: Callable[[T], U], /) -> None:
    """ `for x in arr: fn(x)` """
    for x in arr: fn(x)
    return None

@overload
def find(arr: Iterable[T], fn: Callable[[T], bool], /) -> Optional[T]: ...

@overload
def find(arr: Iterable[T], fn: Callable[[T], bool], /, *, unique: Literal[True]=True) -> Optional[T]: ...

@overload
def find(arr: Iterable[T], fn: Callable[[T], bool], /, *, strict: Literal[True]=True) -> T: ...

@overload
def find(arr: Iterable[T], fn: Callable[[T], bool], /, *, unique: bool, strict: Literal[False]=False) -> Optional[T]: ...

@overload
def find(arr: Iterable[T], fn: Callable[[T], bool], /, *, unique: bool, strict: Literal[True]=True) -> T: ...

def find(arr: Iterable[T], fn: Callable[[T], bool], /, *, unique: bool=False, strict: bool=False):
    matched = filter(arr, fn)
    if (strict and not matched):
        raise RuntimeError(LogMsg(
            "No values satisfying filter function.",
            iterable_received=lute.annotate(arr),
            fn_received=lute.annotate(fn)
        ))
    if (unique and len(matched) > 1):
        raise RuntimeError(LogMsg(
            "Found multiple values satisfying filter function.",
            iterable_received=lute.annotate(arr),
            fn_received=lute.annotate(fn)
        ))
    return None if not matched else matched[0]

def every(arr: Iterable[T], fn: Callable[[T], bool]=lambda x: bool(x), /) -> bool:
    """ *`@returns`* `all(map(arr, fn))` """
    return all(map(arr, fn))

def some(arr: Iterable[T], fn: Callable[[T], bool]=lambda x: bool(x), /) -> bool:
    """ *`@returns`* `any(map(arr, fn))` """
    return any(map(arr, fn))


_MISSING = object()

@overload
def reduce(
    arr: Iterable[T],
    fn: Callable[[T, T, int], T],
    /,
) -> T: ...

@overload
def reduce(
    arr: Iterable[T],
    fn: Callable[[U, T, int], U],
    acc: U,
    /,
) -> U: ...

@overload
def reduce(
    arr: Iterable[T],
    fn: Callable[[U, T, int], U],
    acc: U,
    /,
    start_offset:int=0,
) -> U: ...

def reduce(
    arr: Iterable[T],
    fn: Callable[..., Any],
    acc=_MISSING,
    /,
    start_offset:int=0,
):
    it: Iterator[T] = iter(arr)
    start = 0
    if acc is _MISSING:
        try:
            acc = next(it)
        except StopIteration:
            raise ValueError(
                "[reduce] accumulator omitted and iterable is empty"
            ) from None
        start = 1

    for i, item in enumerate(it, start=start+start_offset):
        acc = fn(acc, item, i)
    return acc



def isArray(arr: Any) -> TypeGuard[list[Any] | tuple[Any,...]]:
    return isinstance(arr, (list, tuple))

def isNonAtomicSequence(arr: Any) -> TypeGuard[Sequence[Any]]:
    return (not _is_atomic(arr) and (isinstance(arr, Sequence)))
