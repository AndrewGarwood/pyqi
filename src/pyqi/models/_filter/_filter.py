"""
*`@file`* `models/_filter`
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import (Any, Self, TypedDict, TypeVar)
from lute import LogMsg, annotate
from ... import _json as Json
from ...utils import export
from .operator import Operator

class FilterDict(TypedDict):
    field: str
    operator: str
    value: Any | list[Any]

@dataclass
class Filter(Json.Serial[FilterDict]):
    """
    ```
    field: str
    operator: Operator
    value: list[VT]
    ```
    """
    field: str
    operator: Operator
    value: Any

    def __init__(self, field: str, operator: str | Operator, value: Any=None):
        self.field = field
        self.operator = Operator.resolve(operator)
        self.value = value

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
                value=data['value']
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
            "value": Json.serialize(self.value)
        }

__all__ = export(FilterDict, Filter)