"""
*`@file`* `_array/_find.py`
"""
from __future__ import annotations
from collections.abc import (Iterable, Iterator)
from typing import (
    Callable, Literal, Optional, TypeVar, overload
)
from lute import (LogMsg, annotate)
from ..utils.module import export

T = TypeVar('T')
U = TypeVar('U')

@overload
def find(
    arr: Iterable[T], 
    fn: Callable[[T], bool], 
    /
) -> Optional[T]: ...

@overload
def find(
    arr: Iterable[T], 
    fn: Callable[[T], bool], 
    /, 
    *, 
    unique: Literal[True]=True
) -> Optional[T]: ...

@overload
def find(
    arr: Iterable[T], 
    fn: Callable[[T], bool], 
    /, 
    *, 
    strict: Literal[True]=True
) -> T: ...

@overload
def find(
    arr: Iterable[T], 
    fn: Callable[[T], bool], 
    /, 
    *, 
    unique: bool, 
    strict: Literal[False]=False
) -> Optional[T]: ...

@overload
def find(
    arr: Iterable[T], 
    fn: Callable[[T], bool], 
    /, 
    *, 
    unique: bool, 
    strict: Literal[True]=True
) -> T: ...

def find(
    arr: Iterable[T], 
    fn: Callable[[T], bool], 
    /, 
    *, 
    unique: bool=False, 
    strict: bool=False
):
    matched = [x for x in arr if fn(x)]
    if (strict and not matched):
        raise RuntimeError(LogMsg(
            "No values satisfying filter function.",
            iterable_received=annotate(arr),
            fn_received=annotate(fn)
        ))
    if (unique and len(matched) > 1):
        raise RuntimeError(LogMsg(
            "Found multiple values satisfying filter function.",
            iterable_received=annotate(arr),
            fn_received=annotate(fn)
        ))
    return None if not matched else matched[0]


__all__ = export(find)