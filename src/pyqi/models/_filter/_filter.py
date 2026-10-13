"""
*`@file`* `models/_filter`
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import (Any, Self, TypedDict, NotRequired, TypeGuard, Mapping)
from lute import LogMsg, annotate
from ... import _json as Json
from ...utils import export
from ...validation import guard
from .operator import Operator

class FilterDict(TypedDict):
    field: str
    operator: str
    value: Any
    negate: NotRequired[bool]

def is_filter_dict(value: Any, /) -> TypeGuard[FilterDict]:
    return (
        isinstance(value, Mapping)
        and guard.is_non_empty_string(value.get("field", None))
        and Operator.can_resolve(value.get("operator", None))
        and "value" in value.keys()
        and ("negate" not in value.keys() or isinstance(value["negate"], bool))
    )

@dataclass
class Filter(Json.Serial[FilterDict]):
    """
    ```
    field: str
    operator: Operator
    value: list[VT]
    negate: bool = False 
    # maybe useful if want to indicate that should take inverse of statement 
    # (assuming don't want to use the corresponding operator or it doesn't exist)
    # e.g. building pl.Expr, expr = (expr.not_() if f.negate else expr)
    ```
    """
    field: str
    operator: Operator
    value: Any
    negate: bool

    def __init__(self, field: str, operator: str | Operator, value: Any=None, negate: bool=False):
        self.field = field
        self.operator = Operator.resolve(operator)
        self.value = value
        self.negate = negate

    @classmethod
    def from_dict(
        cls, 
        data: FilterDict | dict[str, Any], 
        /, 
    ) -> Self:
        try:
            return cls(
                field=data['field'],
                operator=data['operator'],
                value=data['value'],
                negate=data.get('negate', False)
            )
        except Exception as e:
            raise RuntimeError(LogMsg.err(
                e, 
                received=Json.serialize(data), 
            )) from e

    def to_dict(self) -> FilterDict | dict[str, Any]:
        return {
            "field": self.field,
            "operator": str(self.operator),
            "value": Json.serialize(self.value),
            "negate": self.negate
        }

__all__ = export(FilterDict, Filter, is_filter_dict)