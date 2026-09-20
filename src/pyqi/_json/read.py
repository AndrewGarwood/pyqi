"""
*`@file`* `_json/read`

*read* `json` values from `str | Path`
"""
import json
from pathlib import Path
from lute import LogMsg, annotate
from ..fs import (StrPath)
from typing import (TypeVar)
from .types import (
    JsonObject, 
    JsonScalar, 
    JsonValue, 
    JsonArray
)
T = TypeVar('T', bound=JsonScalar)

def file(path: StrPath, /, **kwargs) -> JsonValue:
    try:
        with Path(path).open("r", encoding="utf-8") as f:
            return json.load(f, **kwargs)
    except Exception as e:
        raise RuntimeError(LogMsg.err(e, received=annotate(path))) from e

def object(path: StrPath, /, **kwargs) -> JsonObject:
    try:
        with Path(path).open('r', encoding="utf-8") as f:
            value: JsonObject = json.load(f, **kwargs)
            if (not isinstance(value, dict)):
                raise TypeError(LogMsg.bad_arg(
                    value, "json.load(path)", "Invalid JsonObject", dict
                ))
            return value
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e, 
            path=annotate(path), 
            kwargs=str(kwargs)
        )) from e

def array(path: StrPath, /, **kwargs) -> JsonArray:
    try:
        with Path(path).open('r', encoding="utf-8") as f:
            value: JsonArray = json.load(f, **kwargs)
            if (not isinstance(value, list)):
                raise TypeError(LogMsg.bad_arg(
                    value, "json.load(path)", "value is not instanceof list", list
                ))
            return value
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e, 
            path=annotate(path), 
            kwargs=str(kwargs)
        )) from e

def scalar(path: StrPath, expected_type: type[T], /, **kwargs) -> JsonScalar:
    try:
        with Path(path).open('r', encoding="utf-8") as f:
            value: JsonValue = json.load(f, **kwargs)
            if (expected_type is int and isinstance(value, bool)):
                raise TypeError(LogMsg.bad_arg(
                    value, "json.load(path)", "value is not an int", int
                ))
            if (not isinstance(value, expected_type)):
                raise TypeError(LogMsg.bad_arg(
                    value, "json.load(path)", 
                    "value is not expected scalar type", expected_type
                ))
            return value
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e, 
            path=annotate(path), 
            expected_type=str(expected_type), 
            kwargs=str(kwargs)
        )) from e