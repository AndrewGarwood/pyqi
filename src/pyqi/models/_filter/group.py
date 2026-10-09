"""
*`@file`* `models/_filter/group`
"""
from __future__ import annotations
from dataclasses import dataclass, field as _field
from .._enum import BaseStrEnum
from typing import (Any, Self, TypedDict)
from lute import LogMsg
from ... import _json as Json
from ...utils import export

from ._filter import (FilterDict, Filter)


class FilterGroupOperator(BaseStrEnum):
    AND = "AND"
    OR = "OR"

class FilterGroupDict(TypedDict):
    group_operator: FilterGroupOperator
    filters: list[FilterDict]


@dataclass
class FilterGroup(Json.Serial[FilterGroupDict]):
    group_operator: FilterGroupOperator = FilterGroupOperator.AND
    filters: list[Filter[Any]] = _field(default_factory=list)

    @classmethod
    def from_dict(cls, data: FilterGroupDict | dict[str, Any], /,) -> Self:
        try:
            return cls(
                group_operator=FilterGroupOperator.resolve(data['group_operator']),
                filters=[Filter.from_dict(x) for x in data['filters']]
            )
        except Exception as e:
            raise RuntimeError(LogMsg.err(e, received=Json.serialize(data))) from e

    def to_dict(self) -> FilterGroupDict | dict[str, Any]:
        return {
            "filters": [(x.to_dict()) for x in self.filters],
            "group_operator": str(self.group_operator)
        }

__all__ = export(FilterGroupOperator, FilterGroupDict, FilterDict)