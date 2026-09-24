"""
*`@file`* `validation/require/number`
"""

from ..guard import number as Number
from typing import Any
from lute import LogMsg
from pyqi._utils import export_symbols

def integer(value: Any, /, name:str='arg'):
    if (not Number.is_integer(value)):
        raise TypeError(LogMsg.bad_arg(
            value, name, "integer value is required", Number.Integer
        ))
    return value

def float(value: Any, /, name:str='arg'):
    if (not Number.is_float(value)):
        raise TypeError(LogMsg.bad_arg(
            value, name, "float value is required", Number.Float
        ))
    return value

def number(value: Any, /, name:str='arg'):
    if (not Number.is_number(value)):
        raise TypeError(LogMsg.bad_arg(
            value, name, "number is required", Number.Integer, Number.Float
        ))
    return value

def positive_integer(value: Any, /, name:str='arg'):
    if not (Number.is_integer(value) and value > 0):
        raise ValueError(LogMsg.bad_arg(
            value, 
            name, 
            "positive integer is required", "int > 0"
        ))
    return value

def positive_number(value: Any, /, name: str='arg'):
    if (not Number.is_positive_number(value)):
        raise ValueError(LogMsg.bad_arg(
            value, name, "positive number is required", 
            "(int | float) > 0"
        ))
    return value

__all__ = [ 
    *export_symbols(integer, float, number, positive_number, positive_integer)
] # type: ignore