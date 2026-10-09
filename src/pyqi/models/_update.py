"""
*`@file`* `models/_update`
"""
from __future__ import annotations
from datetime import datetime, date
from dataclasses import dataclass
from collections.abc import Mapping
from typing import (Any, NotRequired, Self, TypedDict, Optional, TypeVar, Generic)
from lute import LogMsg
from .. import _json as Json, _dt as dt
from ..utils import export
T = TypeVar('T') # , bound=Mapping

class UpdateManifestDict(TypedDict):
    success: bool
    started_at: str
    completed_at: str
    ref_date_used: str # mb rename to key_date or put in updated: dict or other type param
    updated: Any
    message: NotRequired[str | None]
    error: NotRequired[str | None]


@dataclass
class UpdateManifest(Json.Serial[UpdateManifestDict], Generic[T]):
    success: bool
    started_at: datetime
    completed_at: datetime
    ref_date_used: date
    updated: T
    message: Optional[str]=None
    error: Optional[str]=None

    @classmethod
    def from_dict(cls, data: UpdateManifestDict | dict[str, Any]) -> Self:
        try:
            return cls(
                success=data['success'],
                started_at=dt.Datetime.parse(data['started_at']),
                completed_at=dt.Datetime.parse(data['completed_at']),
                ref_date_used=dt.Date.parse(data['ref_date_used']),
                updated=data.get('updated', dict()),
                message=data.get('message'),
                error=data.get('error'),
            )
        except Exception as e:
            raise RuntimeError(LogMsg.err(error=e)) from e


__all__ = export(UpdateManifestDict, UpdateManifest)