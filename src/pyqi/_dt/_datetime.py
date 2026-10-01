"""
*`@file`* `_dt/_datetime.py`
"""
from __future__ import annotations
import datetime as dt
from typing import (Literal,  Optional, overload)
from zoneinfo import ZoneInfo
import dateutil
from lute import LogMsg
from .constants import (DateValue, EXCEL_EPOCH)


def now(tz: Optional[ZoneInfo]=None,/):
    return dt.datetime.now(tz)

def strftime(d: dt.datetime, fmt: str, /) -> str: # unnecessary function, but mb useful when import module...
    return d.strftime(fmt)


def strptime(s: str, fmt: Optional[str]=None, /) -> dt.date:
    return dt.datetime.strptime(s, fmt) if fmt else parse(s)


def parse(date_str: str, /, parserinfo: Optional[dateutil.parser.parserinfo]=None, **kwargs) -> dt.datetime:
    return dateutil.parser.parse(
        date_str, 
        parserinfo=parserinfo, 
        **kwargs
    )

@overload
def resolve(d: DateValue, /)  -> Optional[dt.datetime]: ...

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
            raise RuntimeError(LogMsg.err(e, d=str(d), strict=strict))
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
    def string(v: str, fmt: str, /, year: Optional[int]=None, month: Optional[int]=None, day: Optional[int]=None):
        _dt = dt.datetime.strptime(v, fmt)
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
    def days_since_xl_epoch(v: int | float, /):
        return EXCEL_EPOCH + dt.timedelta(days=float(v))

class To():
    @staticmethod
    def date(_dt: dt.datetime, /):
        return _dt.date()
    
    @staticmethod
    def string(
        _dt: dt.datetime, 
        fmt: Optional[str]=None, 
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