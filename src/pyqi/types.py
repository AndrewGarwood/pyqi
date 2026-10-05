"""
*`@file`* `pyqi/types`
"""
from enum import (StrEnum, IntEnum)
from typing import (Iterable, TypeAlias, TypeGuard, Any, TypeVar)
from ._utils import export
T = TypeVar('T')
StrEnumT = TypeVar("StrEnumT", bound=StrEnum)
IntEnumT = TypeVar("IntEnumT", bound=IntEnum)

Primitive: TypeAlias = str | int | float | bool | None

def is_primitive(value: Any, /) -> TypeGuard[Primitive]:
    return value is None or isinstance(value, (str, int, float, bool))

Atomic: TypeAlias = str | bytes | bytearray

def is_atomic(value: Any, /) -> TypeGuard[Atomic]:
    return isinstance(value, (str, bytes, bytearray))

Arbitrary: TypeAlias = T | Iterable[T]
Resolved: TypeAlias = tuple[T, ...]

def resolve_arbitrary(
    value: Arbitrary[T], 
    /, 
    atomic_to_singleton: bool=True, 
    none_to_empty: bool=True
) -> tuple[T, ...]:
    """ 
    - assumes 1D Iterable `if value is not T`
    - *`@param`* `value (T | Iterable[T, ...])`
    - *`@param`* `atomic_to_singleton (bool, default=True)` 
        - whether to return `tuple[T] (length 1)`
        or to pass `value` into `tuple` constructor when `value` is `Atomic`
        - `Atomic: TypeAlias = str | bytes | bytearray`
    - *`@param`* `none_to_empty (bool, default=True)` - if `true` and `value is None` return empty tuple
    - *`@returns`* `tuple[T,...]` i.e. `Resolved[T]`
    """
    if (none_to_empty and value is None): 
        return tuple()
    if (atomic_to_singleton and is_atomic(value)):
        return (value,) # type: ignore
    return (value,) if not isinstance(value, (Iterable)) else tuple(value)

FlexStr: TypeAlias = StrEnumT | str
FlexInt: TypeAlias = IntEnumT | int


class cached_classproperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if owner is None:
            return self
        # Compute the value using the class (owner)
        value = self.func(owner)
        # Cache the calculated value directly onto the class, overwriting the descriptor
        setattr(owner, self.func.__name__, value)
        return value


__all__ = export(
    "Primitive", "Atomic", is_primitive, is_atomic, 
    "Arbitrary", "Resolved", resolve_arbitrary, 
    "FlexStr", "FlexInt", 
    cached_classproperty
)