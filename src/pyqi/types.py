"""
*`@file`* `pyqi/types`
"""

from typing import (Iterable, TypeAlias, TypeGuard, Any, TypeVar)
T = TypeVar('T')

Primitive: TypeAlias = str | int | float | bool | None

def is_primitive(value: Any, /) -> TypeGuard[Primitive]:
    return value is None or isinstance(value, (str, int, float, bool))

Atomic: TypeAlias = str | bytes | bytearray

def is_atomic(value: Any, /) -> TypeGuard[Atomic]:
    return isinstance(value, (str, bytes, bytearray))

Arbitrary: TypeAlias = T | Iterable[T]
Resolved: TypeAlias = tuple[T, ...]

def resolve_arbitrary(value: Arbitrary[T], /, atomic_singleton: bool=True) -> tuple[T, ...]:
    """ 
    - assumes 1D Iterable `if value is not T`
    - *`@param`* `value (T | Iterable[T, ...])`
    - *`@param`* `atomic_is_singleton (bool, default=True)` - whether to return `tuple[T] (length 1)`
        or to pass value into tuple constructor when value is `Atomic`
        - `Atomic: TypeAlias = str | bytes | bytearray`
    - *`@returns`* `tuple[T,...]` i.e. `Resolved[T]`
    """
    if (atomic_singleton and is_atomic(value)):
        return (value,) # type: ignore
    return (value,) if not isinstance(value, (Iterable)) else tuple(value)