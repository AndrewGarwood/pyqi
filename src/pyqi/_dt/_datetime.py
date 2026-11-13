"""
*`@file`* `_dt/_datetime.py`
"""
from __future__ import annotations
import datetime as dt
from typing import (Literal, overload)
from zoneinfo import ZoneInfo
import dateutil
from lute import LogMsg
from .types import (DateValue)
from .constants import (EXCEL_EPOCH, EXCEL_1904_EPOCH)
from pyqi.utils.module import export


def now(tz: ZoneInfo | None=None,/):
    return dt.datetime.now(tz)

def strftime(d: dt.datetime, fmt: str, /) -> str: # redundant, but mb useful when import module...
    return d.strftime(fmt)


def strptime(s: str, fmt: str | None=None, /) -> dt.datetime:
    return dt.datetime.strptime(s, fmt) if fmt else parse(s)


def parse(
    dt_str: str, 
    /, 
    parserinfo: dateutil.parser.parserinfo | None=None, 
    **kwargs
) -> dt.datetime:
    return dateutil.parser.parse(
        dt_str, 
        parserinfo=parserinfo, 
        **kwargs
    )

@overload
def resolve(d: DateValue, /)  -> dt.datetime | None: ...

@overload
def resolve(d: DateValue, /, strict: Literal[True]) -> dt.datetime: ...

def resolve(d: DateValue, /, strict: bool=False):
    """
    *`@returns`*
    - `dateutil.parser.parse(d) if isinstance(d, str)`
    - `d if isinstance(d, dt.datetime)`
    - `Datetime.From.date(d) if isinstance(d, dt.date)`
    - `else None`
    """
    try:
        if isinstance(d, str): 
            return dateutil.parser.parse(d)
        result = (
            d if isinstance(d, dt.datetime)
            else From.date(d) if isinstance(d, dt.date)
            else None
        )
        if (result is None and strict):
            raise ValueError(f"Unable to resolve value '{d}' to datetime")
        return result
    except Exception as e:
        if (strict): 
            raise RuntimeError(LogMsg.err(
                e, 
                d=str(d), 
                strict=strict
            )) from e
        return None
    
class From():
    @staticmethod
    def date(v: dt.date, /, hour: int=0, minute: int=0, second: int=0, microsecond: int=0):
        return dt.datetime(
            v.year, v.month, v.day, 
            hour=hour, 
            minute=minute, 
            second=second, 
            microsecond=microsecond
        )

    @staticmethod
    def string(
        v: str, 
        /, 
        fmt: str | None=None, 
        year: int | None=None, 
        month: int | None=None, 
        day: int | None=None
    ):
        _dt = strptime(v, fmt)
        return (
            dt.datetime(
                year=year or _dt.year,
                month=month or _dt.month,
                day=day or _dt.day,
                hour=_dt.hour,
                minute=_dt.minute,
                second=_dt.second,
                microsecond=_dt.microsecond
            )
        )
        


    @staticmethod
    def days_since_xl_epoch(v: int | float, /, *, use_1904_epoch: bool=False):
        """
        *`@returns`* 
        `epoch_datetime + dt.timedelta(days=float(serial))`
        - where `serial` = `v + 1` if `(not use_1904_epoch and v < 60)` else `v`
        ```
        EXCEL_EPOCH: datetime = datetime(1899, 12, 30)
        EXCEL_1904_EPOCH: datetime = dt.datetime(1904, 1, 1)
        ```
        """
        if (not use_1904_epoch):
            serial = (v + 1 if v < 60 else v)
            return EXCEL_EPOCH + dt.timedelta(days=float(serial))
        else:
            return EXCEL_1904_EPOCH + dt.timedelta(days=float(v))

class To():
    @staticmethod
    def date(_dt: dt.datetime, /):
        return _dt.date()
    
    @staticmethod
    def string(
        _dt: dt.datetime, 
        fmt: str | None=None, 
        /, 
    ):
        return (
            _dt.strftime(fmt) if isinstance(fmt, str) 
            else _dt.isoformat()
        )


def isostamp(
    include_time: bool=True,
    *, 
    part_sep: Literal['.', '-', '_'] = '.', 
    datetime_sep: Literal['T', ' ']=' ',
    fs_compatible: bool=True
) -> str:
    s = dt.datetime.now().isoformat(sep=datetime_sep)
    if part_sep != '-':
        s = s.replace('-', part_sep)
    if fs_compatible: 
        s = s.replace(':', part_sep)
        # TODO: define a set of incompatible chars and replace with empty space
    return s if include_time else s.split(datetime_sep)[0]

__all__ = export(From, To, isostamp, resolve, strptime, strftime, now)