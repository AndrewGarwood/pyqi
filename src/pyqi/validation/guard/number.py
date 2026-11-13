"""
*`@file`* `validation/guard/number`
"""
from typing import (Any, TypeGuard, TypeAlias)
from pyqi.utils.module import export

Integer: TypeAlias = int
Float: TypeAlias = float

def is_integer(value: Any,/) -> TypeGuard[int]:
    return not isinstance(value, bool) and isinstance(value, int)

def is_float(value: Any,/) -> TypeGuard[float]:
    return isinstance(value, float)

def is_number(value: Any, /) -> TypeGuard[int | float]:
    """
    *`@returns`* 
    `not isinstance(value, bool) and isinstance(value, (int, float))`
    """
    return not isinstance(value, bool) and isinstance(value, (int, float))

def is_positive_number(value: Any, /) -> TypeGuard[int | float]:
    return is_number(value) and value > 0

def is_positive_integer(value: Any, /) -> TypeGuard[int]:
    return isinstance(value, int) and value > 0

def is_non_negative_number(value: Any, /) -> TypeGuard[int | float]:
    return is_number(value) and value >=0


__all__ = export(
    "Integer", 
    "Float",
    is_integer, 
    is_float, 
    is_number, 
    is_positive_integer, 
    is_positive_integer, 
    is_non_negative_number,
)