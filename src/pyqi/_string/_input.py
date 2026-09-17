
from __future__ import annotations
from typing import (Sequence, TypeAlias)
from lute import LogMsg

StrInput: TypeAlias = str | Sequence[str]
ResolvedStrInput: TypeAlias = tuple[str, ...]
""" `return` type of `resolve_str_input(s: StrInput, /)` """

def resolve_str_input(s: StrInput, /, require_non_empty: bool=True) -> tuple[str, ...]:
    result: tuple[str,...] | None = None
    if isinstance(s, str): 
        result = (s,)
    elif isinstance(s, list):
        result = tuple(s)
    elif isinstance(s, tuple):
        result = s
    else:
        raise ValueError(LogMsg(
            f"Unsupported type for StrInput.",
            expected="str | Sequence[str]",
            received=f"{type(s)=}"
        ))
    if (require_non_empty and not all(result)):
        raise ValueError(LogMsg(
            f"Received invalid StrInput",
            received=s,
            resolved=result,
            require_non_empty=require_non_empty
        ))
    return result