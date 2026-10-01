"""
*`@file`* `_dt/_date.py`
"""
from __future__ import annotations
from pathlib import Path
import calendar
from collections.abc import Collection
import calendar
import datetime as dt
from dateutil.relativedelta import relativedelta
from typing import (Literal, Callable, Optional, TypedDict, NotRequired, overload)
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from dateutil import parser
from .constants import Weekday, DateValue
from lute import LogMsg
from .. import _array as Array



def _default_get_date_str(s: str, /) -> str: return s[:10]

def strftime(d: dt.date, fmt: str, /) -> str: return d.strftime(fmt)

def strptime(s: str, fmt: Optional[str]=None, /) -> dt.date:
    return dt.datetime.strptime(s, fmt).date() if fmt else parse(s)

def today() -> dt.date: return dt.date.today()

@overload
def resolve(d: DateValue, /) -> Optional[dt.date]: ...

@overload
def resolve(d: DateValue, /, strict: Literal[True]) -> dt.date: ...

def resolve(d: DateValue, /, strict: bool=False): # , default: Optional[dt.date]=None
    """
    *`@returns`*
    - `parse(d) if isinstance(d, str)`
    - `d.date() if isinstance(d, dt.datetime)`
    - `d if isinstance(d, dt.date)`
    - `else None`
    """
    result = (
        parse(d) if isinstance(d, str)
        else d.date() if isinstance(d, dt.datetime)
        else d if isinstance(d, dt.date)
        else None
    )
    if (result is None and strict):
        raise ValueError(LogMsg.bad_arg(
            d, "date_value", "Unable to resolve value to date", 
            dt.date, dt.datetime, str
            ))
    return result

def strict_resolve_date(d: DateValue, /) -> dt.date:
    """
    *`@returns`*
    - `parse(d) if isinstance(d, str)`
    - `d.date() if isinstance(d, dt.datetime)`
    - `d if isinstance(d, dt.date)`
    - `else raise ValueError`
    """
    result = (
        parse(d) if isinstance(d, str)
        else d.date() if isinstance(d, dt.datetime)
        else d if isinstance(d, dt.date)
        else None
    )
    if result is None:
        raise ValueError(LogMsg(f"Unable to resolve value '{d}' to date object"))
    return result

def parse(date_str: str, /, parserinfo: Optional[parser.parserinfo]=None, **kwargs) -> dt.date:
    try:
        return parser.parse(date_str, parserinfo=parserinfo, **kwargs)
    except Exception as e:
        raise ValueError(LogMsg.err(
            e,
            date_str=date_str,
            parserinfo=str(parserinfo),
            kwargs=str(kwargs)
        )) from e
        
        
class From():
    @staticmethod
    def datetime(_dt: dt.datetime, /) -> dt.date: # unnecessary, but for completeness
        return _dt.date()

    @staticmethod
    def string(
        s: str, 
        fmt: Optional[str]=None, 
        /, 
        year: Optional[int]=None, 
        month: Optional[int]=None, 
        day: Optional[int]=None
    ) -> dt.date:
        _date = (
            parse(s) if fmt is None 
            else dt.datetime.strptime(s, fmt).date()
        )
        return dt.date(
            year=year or _date.year,
            month=month or _date.month,
            day=day or _date.day
        )
    @staticmethod
    def pathstem(s: str | Path, fmt: str, /, get_date_part: Callable[[str], str]=_default_get_date_str):
        original_value = s
        if isinstance(s, Path):
            path_parts = s.parts
            stem = path_parts[len(path_parts)-1]
        else:
            stem = s
        date_part: str = "None"
        try:
            date_part = get_date_part(stem)
            return From.string(date_part, fmt)
        except Exception as e:
            raise Exception(LogMsg.err(
                e,
                original_value=str(original_value),
                stem=stem,
                fmt=fmt,
                get_date_part=f"{str(get_date_part)=}, {get_date_part.__name__=}",
                date_part=date_part,
            )) from e

    @staticmethod
    def parts(year: int, month: int, day: int,):
        return dt.date(year=year, month=month, day=day)


class To():
    @staticmethod
    def datetime(
        d: dt.date, 
        /, 
        hour: Optional[int]=None, 
        minute: Optional[int]=None, 
        second: Optional[int]=None, 
        microsecond: Optional[int]=None, 
        tzinfo: Optional[ZoneInfo]=None
    ):
        return dt.datetime(
            d.year, 
            d.month, 
            d.day, 
            hour=hour or 0, 
            minute=minute or 0, 
            second=second or 0, 
            microsecond=microsecond or 0,
            tzinfo=tzinfo
        )
    
    @staticmethod
    def string(d: dt.date, fmt: str, /):
        return d.strftime(fmt)


# TODO: make default set of holidays read in from file...
def offset_business_day(
    ref: Optional[DateValue] = None,
    days: int = 1,
    holidays: Optional[Collection[DateValue]] = None,
) -> dt.date:
    """
    Offset `ref` by a signed number of business days.

    Business days are Monday-Friday, excluding dates supplied in
    `holidays`. The reference date is not counted as an offset day.

    Args:
        ref:
            Reference date. If a datetime is supplied, its date component
            is used. Defaults to today's date.
        days:
            Signed number of business days by which to offset `ref`.

            - Positive values move forward.
            - Negative values move backward.
            - Zero returns `ref` unchanged.
        holidays:
            Optional collection of dates that should not be considered
            business days.

    Returns:
        The date obtained after moving by `days` business days.

    Examples:
        >>> offset_business_day(dt.date(2026, 8, 7), days=1)
        datetime.date(2026, 8, 10)

        >>> offset_business_day(dt.date(2026, 8, 10), days=-1)
        datetime.date(2026, 8, 7)

        >>> offset_business_day(dt.date(2026, 8, 7), days=3)
        datetime.date(2026, 8, 12)

        >>> offset_business_day(
        ...     dt.date(2026, 7, 2),
        ...     days=1,
        ...     holidays={dt.date(2026, 7, 3)},
        ... )
        datetime.date(2026, 7, 6)

        >>> offset_business_day(dt.datetime(2026, 8, 7, 15, 30), days=0)
        datetime.date(2026, 8, 7)
    """

    if not isinstance(days, int):
        raise TypeError(LogMsg(
            f"days must be an integer, got {type(days).__name__}"
        ))
    ref_date = resolve(ref) if ref else today()
    if not isinstance(ref_date, dt.date):
        raise TypeError(LogMsg(
            f"ref must be a date, datetime, valid date str, or None, "
            f"{ref=} resolved to {type(ref_date).__name__} = {ref_date}"
        ))

    if days == 0: return ref_date
    
    _holidays: list[dt.date] = (
        Array.filter_map(list(holidays), resolve)
        if holidays is not None 
        else []
    )
    holiday_set = set(_holidays)
    step = 1 if days > 0 else -1
    delta = dt.timedelta(days=step)

    candidate = ref_date
    remaining = abs(days)

    while remaining:
        candidate += delta
        if candidate.weekday() < 5 and candidate not in holiday_set:
            remaining -= 1

    return candidate


def previous_business_day(
    ref: Optional[DateValue] = None,
    holidays: Optional[Collection[DateValue]] = None,
) -> dt.date:
    """
    Return the business day immediately preceding `ref`

    Business days are Monday-Friday excluding any dates supplied in `holidays`

    Args:
        ref:
            Reference date. Defaults to today's date.
        holidays:
            Optional collection of holiday dates that should not
            be considered business days.

    Returns:
        The previous business day.

    Examples:
        >>> previous_business_day(date(2026, 8, 10)) # Monday August 10th, 2026
        date(2026, 8, 7) # Friday August 7th, 2026

        >>> previous_business_day(
        ...     date(2026, 7, 6),
        ...     holidays={date(2026, 7, 3)},
        ... )
        date(2026, 7, 2)
    """
    return offset_business_day(ref, days=-1, holidays=holidays)


def next_business_day(
    ref: Optional[DateValue] = None,
    holidays: Optional[Collection[DateValue]] = None,
) -> dt.date:
    return offset_business_day(ref, days=1, holidays=holidays)


def last_day_of_month(year: int, month: int) -> dt.date:
    if month == 12:
        next_month = dt.date(year + 1, 1, 1)
    else:
        next_month = dt.date(year, month + 1, 1)
    return next_month - dt.timedelta(days=1)


class ComputeDateDict(TypedDict, total=False):
    anchor: NotRequired[str]
    year_offset: NotRequired[int]
    month_offset: NotRequired[int]
    day_offset: NotRequired[int]
    year: NotRequired[int]
    month: NotRequired[int | str]
    day: NotRequired[int | Literal["first", "last"]]


@dataclass
class ComputeDateOptions():
    anchor: dt.date | None = None
    year_offset: int = 0
    month_offset: int = 0
    day_offset: int = 0
    year: Optional[int]=None
    month: int | str | None = None
    day: int | Literal["first", "last"] | None = None

    @classmethod
    def from_dict(cls, data: ComputeDateDict, /) -> ComputeDateOptions:
        try:
            return cls(
                anchor=parse(data["anchor"]) if "anchor" in data else None,
                year_offset=data.get("year_offset", 0),
                month_offset=data.get("month_offset", 0),
                day_offset=data.get("day_offset", 0),
                year=data.get("year"),
                month=data.get("month"),
                day=data.get("day"),
            )
        except Exception as e:
            raise Exception(LogMsg.err(e,
                received=str(data)
            )) from e


def compute_date(
    *,
    anchor: Optional[DateValue] = None,
    year_offset: int = 0,
    month_offset: int = 0,
    day_offset: int = 0,
    year: Optional[int]=None,
    month: int | str | None = None,
    day: int | Literal["first", "last"] | None = None,
    options: Optional[ComputeDateOptions]=None
) -> dt.date:
    """
    Generic date computation.

    - anchor: base reference date (default today)
    - year_offset: shift years
    - month_offset: shift months
    - day_offset: shift days
    - month: override month (optional)
    - day:
        - int -> fixed day
        - "first" -> first day of period
        - "last" -> last day of period

    Examples:
        compute_date(day_offset=-1)           # yesterday
        compute_date(month_offset=-1)         # same day last month
        compute_date(year_offset=-1)          # same day last year
        compute_date(month="January", day=1)  # Jan 1 current year
    """
    if (options):
        anchor = options.anchor
        year_offset = options.year_offset
        month_offset = options.month_offset
        day_offset = options.day_offset
        year = options.year
        month = options.month
        day = options.day

    base = resolve(anchor, strict=True) if anchor else today()
    
    result = (
        base
        + relativedelta(years=year_offset, months=month_offset)
        + dt.timedelta(days=day_offset)
    )
    year = result.year if year is None else year
    month = (
        list(calendar.month_name).index(month.capitalize()) if isinstance(month, str)
        else (month or result.month)
    )

    if isinstance(day, int):
        return dt.date(year, month, day)
    if isinstance(day, str):
        if day.lower() == "first":
            return dt.date(year, month, 1)
        elif day.lower() == "last":
            return last_day_of_month(year, month)
    return dt.date(year, month, result.day) # default: return same day



def previous_weekday(
    ref: Optional[DateValue],
    weekday: Weekday,
    allow_same_day: bool = True,
    ) -> dt.date:
    
    """
    ex: get most recent Friday when `dt = datetime(2026, 5, 14)` (a Thursday)
    dt is thusrday -> previous Friday is May 8th, 2026

    Note: term "weekday" includes saturday and sunday so it's more like "day of the week"
    """
    if not (Weekday.MONDAY <= weekday <= Weekday.SUNDAY):
        raise ValueError(f"weekday must be in range 0..6 (Mon=0..Sun=6); got {weekday}")
    ref = To.datetime(resolve(ref, strict=True) if ref else today())

    
    current_weekday = ref.weekday()
    delta = (current_weekday - weekday) % 7 # (modulus in python) print(-1 % 7) # 6
    if delta == 0 and not allow_same_day:
        delta = 7
    return (ref - dt.timedelta(days=delta)).date()




def next_weekday(
    ref: Optional[DateValue],
    weekday: Weekday,
    allow_same_day: bool = True,
) -> dt.date:
    """
    Return the next soonest occurrence of `day` ~~at 12:00am (00:00).~~

    Parameters
    ----------
    dt:
        Input datetime (naive or timezone-aware). tzinfo is preserved.
    weekday:
        Desired weekday as an int where Monday=0 ... Sunday=6 (dt.weekday()).
    allow_same_day:
        If True and dt falls on `weekday`, return that same date at 00:00.
        If False, then if dt is on `weekday` but after 00:00, roll forward
        to the following week's `weekday` at 00:00.

    Returns
    -------
    datetime
        A datetime representing the next soonest `weekday` at midnight.

    Notes
    -----
    - If dt is exactly at midnight of the target weekday, the function returns
    dt itself (regardless of allow_same_day).
    """
    if not (Weekday.MONDAY <= weekday <= Weekday.SUNDAY):
        raise ValueError(f"weekday must be in range 0..6 (Mon=0..Sun=6); got {weekday}")
    ref = To.datetime(resolve(ref, strict=True) if ref else today())


    # If caller allows "same weekday", return midnight of dt's date when it matches.
    if allow_same_day and ref.weekday() == weekday:
        return ref.replace(hour=0, minute=0, second=0, microsecond=0)

    # Compute days ahead to reach the target weekday (0..6)
    days_ahead = (weekday - ref.weekday()) % 7

    # Candidate: target weekday at midnight
    candidate = (ref + dt.timedelta(days=days_ahead)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # If candidate is earlier than dt (e.g., dt is target weekday later in the day),
    # then roll forward one week.
    if candidate < ref:
        candidate += dt.timedelta(days=7)

    return candidate.date()

