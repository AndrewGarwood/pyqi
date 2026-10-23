"""
*`@file`* `_dt/types`
"""
from dataclasses import dataclass
import datetime as dt
from typing import Literal, NotRequired, TypedDict, TypeAlias, Self
from dateutil import parser
from lute import Any, LogMsg
from pyqi.utils.module import (export)
from .. import _json as Json

DateValue: TypeAlias = dt.date | dt.datetime | str

class ComputeDateOptionsDict(TypedDict, total=False):
    anchor: NotRequired[str]
    year_offset: NotRequired[int]
    month_offset: NotRequired[int]
    day_offset: NotRequired[int]
    year: NotRequired[int]
    month: NotRequired[int | str]
    day: NotRequired[int | Literal["first", "last"]]


@dataclass
class ComputeDateOptions(Json.Serial[ComputeDateOptionsDict]):
    anchor: dt.date | None = None
    year_offset: int = 0
    month_offset: int = 0
    day_offset: int = 0
    year: int | None=None
    month: int | str | None = None
    day: int | Literal["first", "last"] | None = None

    @classmethod
    def from_dict(cls, data: ComputeDateOptionsDict | dict[str, Any], /) -> Self:
        try:
            return cls(
                anchor=parser.parse(data["anchor"]) if "anchor" in data else None,
                year_offset=data.get("year_offset", 0),
                month_offset=data.get("month_offset", 0),
                day_offset=data.get("day_offset", 0),
                year=data.get("year"),
                month=data.get("month"),
                day=data.get("day"),
            )
        except Exception as e:
            raise Exception(LogMsg.err(
                e,
                received=Json.serialize(data)
            )) from e

__all__ = export(ComputeDateOptionsDict, ComputeDateOptions, "DateValue")