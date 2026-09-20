"""
*`@file`* `_json/load`

*load* `json` values from `(str, bytes, bytearray)`
"""
import json
from lute import (LogMsg, annotate)
from typing import (TypeVar)
from .types import (
    JsonObject, 
    JsonScalar, 
    JsonValue, 
    JsonArray,
    JsonRawSequence
)
T = TypeVar('T', bound=JsonScalar)

def sequence(src: JsonRawSequence, /, **kwargs) -> JsonValue:
    try:
        return json.loads(src, **kwargs)
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e, 
            received=annotate(src)
        )) from e


def object(src: JsonRawSequence, /, **kwargs) -> JsonObject:
    try:
        value: JsonObject = json.loads(src, **kwargs)
        if (not isinstance(value, dict)):
            raise TypeError(LogMsg.bad_arg(
                value, "json.loads(src)", "Invalid JsonObject", dict
            ))
        return value
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e, 
            src=annotate(src), 
            kwargs=str(kwargs)
        )) from e

def array(src: JsonRawSequence, /, **kwargs) -> JsonArray:
    try:
        value: JsonArray = json.loads(src, **kwargs)
        if (not isinstance(value, list)):
            raise TypeError(LogMsg.bad_arg(
                value, "json.loads(src)", "value is not instanceof list", list
            ))
        return value
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e, 
            src=annotate(src), 
            kwargs=str(kwargs)
        )) from e

def scalar(src: JsonRawSequence, expected_type: type[T], /, **kwargs) -> JsonScalar:
    try:
        value: JsonValue = json.loads(src, **kwargs)
        if (expected_type is int and isinstance(value, bool)):
            raise TypeError(LogMsg.bad_arg(
                value, "json.loads(src)", "value is not an int", int
            ))
        if (not isinstance(value, expected_type)):
            raise TypeError(LogMsg.bad_arg(
                value, "json.loads(src)", 
                "value is not expected scalar type", expected_type
            ))
        return value
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e, 
            src=annotate(src), 
            expected_type=str(expected_type), 
            kwargs=str(kwargs)
        )) from e