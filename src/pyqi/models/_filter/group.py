"""
*`@file`* `models/_filter/group`
"""
from __future__ import annotations
from dataclasses import dataclass, field as _field
from .._enum import BaseStrEnum
from typing import (Any, Self, TypedDict, TypeGuard, Mapping)
from lute import LogMsg, bad_arg
from ... import _json as Json
from ...utils import export

from ._filter import (FilterDict, Filter, is_filter_dict)


class LogicalOperator(BaseStrEnum):
    AND = "AND"
    OR = "OR"

class FilterGroupDict(TypedDict):
    operator: str
    filters: list[FilterDict | FilterGroupDict]

def is_filter_group_dict(value: Any, /) -> TypeGuard[FilterGroupDict]:
    return (
        isinstance(value, Mapping)
        and LogicalOperator.can_resolve(value.get("operator", None))
        and isinstance(value.get("filters", None), list)
        and all(is_filter_dict(x) for x in value["filters"])
    )


@dataclass
class FilterGroup(Json.Serial[FilterGroupDict]):
    operator: LogicalOperator = LogicalOperator.AND
    filters: list[Filter | FilterGroup] = _field(default_factory=list)

    @classmethod
    def from_dict(cls, data: FilterGroupDict | dict[str, Any], /,) -> Self:
        try:
            filters: list[Filter | FilterGroup] = []
            for i, item in enumerate(data['filters']):
                if (is_filter_dict(item)):
                    filters.append(Filter.from_dict(item))
                elif (is_filter_group_dict(item)):
                    filters.append(FilterGroup.from_dict(item))
                else:
                    raise ValueError(LogMsg.bad_arg(
                        item, 
                        f"FilterGroupDict['filters'][{i}]",
                        "Invalid filter value", FilterDict, FilterGroupDict
                    ))
            return cls(
                operator=LogicalOperator.resolve(data['operator']),
                filters=filters
            )
        except Exception as e:
            raise RuntimeError(LogMsg.err(e, received=Json.serialize(data))) from e

    def to_dict(self) -> FilterGroupDict | dict[str, Any]:
        return {
            "filters": [(x.to_dict()) for x in self.filters],
            "operator": str(self.operator)
        }

__all__ = export(LogicalOperator, FilterGroupDict, FilterGroup)