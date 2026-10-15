"""
*`@file`* `_array/_reduce`
"""
from __future__ import annotations
from collections.abc import (Iterable, Iterator, Callable)
from typing import (
    Any, TypeVar, overload,
)
from inspect import (signature)
from ..utils.module import export

T = TypeVar('T')
U = TypeVar('U')
K = TypeVar('K')
V = TypeVar('V')


_MISSING = object()

@overload
def reduce(
    arr: Iterable[T],
    fn: Callable[[T, T], T],
    /,
) -> T: ...

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
    fn: Callable[[U, T], U],
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
    _reducer = _wrap_reducer(fn)
    for i, item in enumerate(it, start=start+start_offset):
        acc = _reducer(acc, item, i)
    return acc


def _wrap_reducer(
    fn: Callable[..., Any],
    /,
) -> Callable[[Any, Any, int], Any]:
    """ if applicable, Normalize 2-argument reducer to 3-argument reducer """
    sig = signature(fn)
    try:
        sig.bind(None, None, 0)
    except TypeError:
        try:
            sig.bind(None, None)
        except TypeError:
            raise TypeError(
                "reducer must accept either "
                "(acc, curr) or (acc, curr, index)"
            ) from None
        return lambda acc, curr, _: fn(acc, curr)
    return fn




# ============================================================================
# ...
# ============================================================================
@overload
def reduce_mut(
    arr: Iterable[T],
    fn: Callable[[U, T], None],
    acc: U,
    /,
) -> U: ...


@overload
def reduce_mut(
    arr: Iterable[T],
    fn: Callable[[U, T, int], None],
    acc: U,
    /,
    start_offset: int = 0,
) -> U: ...

def reduce_mut(
    arr: Iterable[T],
    fn: Callable[[U, T, int], None] | Callable[[U, T], None],
    acc: U,
    /,
    start_offset: int = 0,
) -> U:
    """ mutate accumulator in-place then return it """
    _reducer = _wrap_reducer(fn)

    for i, item in enumerate(arr, start=start_offset):
        _reducer(acc, item, i)
    return acc


# ============================================================================
# ...
# ============================================================================
class MutReducer():
    @staticmethod
    def dict(
        fn: Callable[[T], tuple[K, V]],
        /
    ) -> Callable[[dict[K, V], T, int], dict[K, V]]:
        """
        - *`@param`* `fn` - function that generates `K, V` tuple from element of type `T`
        - *`@returns`* `reducer` - populates accumulator `(dict)` with `K, V` entries
        """
        return dict_reducer(fn)

    @staticmethod
    def list(
        fn: Callable[[T], U], 
        /
    ) -> Callable[[list[U], T, int], list[U]]:
        """
        - *`@param`* `fn` - function that generates `U`from element of type `T`
        - *`@returns`* `reducer` - populates accumulator `(list)` with `U` elements
        """
        return list_reducer(fn)

    @staticmethod
    def set(
        fn: Callable[[T], U], 
        /
    ) -> Callable[[set[U], T, int], set[U]]:
        """
        - *`@param`* `fn` - function that generates `U`from element of type `T`
        - *`@returns`* `reducer` - populates accumulator `(set)` with `U` elements
        """
        return set_reducer(fn)


def dict_reducer(
    fn: Callable[[T], tuple[K, V]],
    /
) -> Callable[[dict[K, V], T, int], dict[K, V]]:
    """
    - *`@param`* `fn` - function that generates `K, V` tuple from element of type `T`
    - *`@returns`* `reducer` - populates accumulator `(dict)` with `K, V` entries
    
    Usage:
    ```
    Array.reduce(
        code, # Iterable[str]
        dict_reducer(
            lambda c: (c, ref_date.strftime(c))
        ),
        {}, # dict[str, date]
    )
    ```
    """
    def reducer(
        acc: dict[K, V],
        curr: T,
        _: int,
    ) -> dict[K, V]:
        k, v = fn(curr)
        acc[k] = v
        return acc
    return reducer

def list_reducer(
    fn: Callable[[T], U], 
    /
) -> Callable[[list[U], T, int], list[U]]:
    """
    - *`@param`* `fn` - function that generates `U`from element of type `T`
    - *`@returns`* `reducer` - populates accumulator `(list)` with `U` elements
    
    Usage:
    ```
    Array.reduce(
        files, # Iterable[Path]
        list_reducer(lambda p: p.name),
        [], # list[str]
    )
    ```
    """
    def reducer(
        acc: list[U],
        curr: T,
        _: int,
    ) -> list[U]:
        acc.append(fn(curr))
        return acc
    return reducer

def set_reducer(
    fn: Callable[[T], U], 
    /
) -> Callable[[set[U], T, int], set[U]]:
    """
    - *`@param`* `fn` - function that generates `U`from element of type `T`
    - *`@returns`* `reducer` - populates accumulator `(set)` with `U` elements
    
    Usage:
    ```
    Array.reduce(
        files, # Iterable[Path]
        set_reducer(lambda p: p.name),
        set(), # set[str]
    )
    ```
    """
    def reducer(
        acc: set[U],
        curr: T,
        _: int,
    ) -> set[U]:
        acc.add(fn(curr))
        return acc
    return reducer


__all__ = export(reduce, reduce_mut, MutReducer, dict_reducer, list_reducer, set_reducer)