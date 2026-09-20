"""
*`@file`* `_json/types.py`
"""
from __future__ import annotations
from collections.abc import (Mapping)
from typing import (Any, TypeAlias, TypeVar, TypeGuard)
from ..types import Primitive, is_primitive
from .. import _array as Array

T = TypeVar("T", bound=(Mapping)) # cannot use TypedDict here

JsonRawSequence: TypeAlias = str | bytes | bytearray
JsonScalar: TypeAlias = Primitive
JsonValue: TypeAlias = (
    JsonScalar
    | list["JsonValue"]
    | dict[str, "JsonValue"]
)
""" `= JsonScalar | list[JsonValue] | dict[str, JsonValue]` """
JsonObject: TypeAlias = dict[str, JsonValue]
""" `= dict[str, JsonValue]` """
JsonArray: TypeAlias = list[JsonValue]

JsonDict: TypeAlias = T | dict[str, Any]
"""
- For type check flexibility
- e.g. `T` is `TypedDict`
"""

def is_json_value(value: Any, /) -> TypeGuard[JsonValue]:
    return (is_primitive(value)
    or (Array.isArray(value) and Array.every(value, is_json_value))
    or (
        isinstance(value, (dict)) 
        and Array.every(
            value.keys(), 
            lambda k: isinstance(k, str) and is_json_value(value[k])
        )
    )
)


def is_json_object(value: Any, /) -> TypeGuard[JsonObject]:
    """ *`@returns`* `isinstance(value, dict) and is_json_value(value)` """
    return (isinstance(value, dict) and is_json_value(value))