"""
*`@file`* `validation/require/_string`
"""

from typing import Any
from .. import guard
from lute import LogMsg
from pyqi._utils import export_symbols


def non_empty_string(
    value: Any, 
    /,
    name: str='arg',
) -> None:
    if (not guard.is_non_empty_string(value)):
        raise ValueError(LogMsg.bad_arg(
            value, name, "Non-empty string is required", str
        ))
        

__all__ = [ 
    *export_symbols(non_empty_string)
]  # type: ignore
