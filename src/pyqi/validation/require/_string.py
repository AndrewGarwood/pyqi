"""
*`@file`* `validation/require/_string`
"""

from typing import Any
from lute import LogMsg
from pyqi._utils import export_symbols
from .. import guard


def non_empty_string(
    value: Any, 
    /,
    name: str='arg',
):
    if (not guard.is_non_empty_string(value)):
        raise ValueError(LogMsg.bad_arg(
            value, name, "Non-empty string is required", str
        ))
    return value
        

__all__ = [ 
    *export_symbols(non_empty_string)
]  # type: ignore
