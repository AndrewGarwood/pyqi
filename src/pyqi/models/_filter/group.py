"""
*`@file`* `models/_filter/group`
"""
from __future__ import annotations
from dataclasses import dataclass, field as _field, replace
from .._enum import BaseStrEnum
from typing import (Any, Self, TypedDict, TypeGuard, Mapping)
from lute import LogMsg
from copy import deepcopy
from ... import _json as Json
from ...utils import export

from ._filter import (FilterDict, Filter, is_filter_dict)


class LogicalOperator(BaseStrEnum):
    """
    ```
    AND = "AND"
    OR = "OR"
    ```
    """
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
    """
    - `dataclass()`
    - *`@extends`* `Json.Serial[FilterGroupDict]`
    ```
    operator: LogicalOperator = LogicalOperator.AND
    filters: list[Filter | FilterGroup] = _field(default_factory=list)
    ```
    """
    operator: LogicalOperator = LogicalOperator.AND
    filters: list[Filter | FilterGroup] = _field(default_factory=list)

    @classmethod
    def from_dict(cls, data: FilterGroupDict | dict[str, Any], /,) -> Self:
        try:
            operator = LogicalOperator.resolve(data.get('operator', 'AND'))
            filters: list[Filter | FilterGroup] = []
            for i, item in enumerate(data.get('filters', [])):
                if (is_filter_dict(item)):
                    filters.append(Filter.from_dict(item))
                elif (is_filter_group_dict(item)):
                    filters.append(FilterGroup.from_dict(item))
                else:
                    raise ValueError(LogMsg.bad_arg(
                        item, 
                        f"FilterGroupDict[filters][{i}]",
                        "Invalid array element", 
                        FilterDict, FilterGroupDict
                    ))
            return cls(
                operator=operator,
                filters=filters
            )
        except Exception as e:
            raise RuntimeError(LogMsg.err(e,
                f"Failed to construct {cls.__name__} from dictionary", 
                received=Json.serialize(data)
            )) from e

    def to_dict(self) -> FilterGroupDict | dict[str, Any]:
        return {
            "operator": str(self.operator),
            "filters": [(x.to_dict()) for x in self.filters],
        }

    def valid_filter_items(
        self, 
        valid_fields: set[str], 
        /, 
        _raise_on_empty: bool=True
    ):
        """
        instance method that calls static `FilterGroup.get_valid_filter_items()`
        """
        return FilterGroup.get_valid_filter_items(
            self.filters,
            valid_fields,
            _raise_on_empty=_raise_on_empty
        )
    
    @staticmethod
    def get_valid_filter_items(
        items: list[Filter | FilterGroup], 
        valid_fields: set[str], 
        /, 
        _raise_on_empty: bool=True
    ) -> list[Filter | FilterGroup]:
        valid_filters: list[Filter | FilterGroup] = []
        for item in items:
            if (isinstance(item, Filter)):
                if (item.field in valid_fields): valid_filters.append(item)
                continue
            _filters = FilterGroup.get_valid_filter_items(item.filters, valid_fields)
            if (_filters):
                valid_filters.append(item.with_filters(_filters))
        if (not valid_filters and _raise_on_empty):
            raise ValueError(LogMsg(
                f"self.filters did not contain any elements with valid fields",
                valid_fields=list(valid_fields)
            ))
        return valid_filters

    def with_filters(
        self, 
        filters: list[Filter | FilterGroup], 
        /,
        operator: LogicalOperator | None = None
    ) -> FilterGroup:
        """
        *`@returns`*
        ```
        replace(
            self, 
            operator=operator or self.operator,
            filters=filters,
        )
        ```
        """
        return replace(
            self, 
            operator=operator or self.operator,
            filters=filters,
        )
    
__all__ = export(LogicalOperator, FilterGroupDict, FilterGroup)