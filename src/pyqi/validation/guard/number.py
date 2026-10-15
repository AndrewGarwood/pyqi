"""
*`@file`* `validation/guard/number`
"""
from typing import (Any, TypeGuard, TypeAlias)

Integer: TypeAlias = int
Float: TypeAlias = float

def is_integer(value: Any,/) -> TypeGuard[int]:
    return isinstance(value, int)

def is_float(value: Any,/) -> TypeGuard[float]:
    return isinstance(value, float)

def is_number(value: Any, /) -> TypeGuard[int | float]:
    return isinstance(value, (int, float))

def is_positive_number(value: Any, /) -> TypeGuard[int | float]:
    return is_number(value) and value > 0

def is_non_negative_number(value: Any, /) -> TypeGuard[int | float]:
    return is_number(value) and value >=0