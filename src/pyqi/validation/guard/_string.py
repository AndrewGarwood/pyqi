"""
*`@file`* `validation/guard/_string`
"""
from enum import StrEnum
from typing import (Any, TypeGuard, TypeVar)

StringT = TypeVar('StringT', bound=str | StrEnum)

def is_non_empty_string(value: StringT | Any, /) -> TypeGuard[StringT]:
    return (isinstance(value, str) and bool(value.strip()))
