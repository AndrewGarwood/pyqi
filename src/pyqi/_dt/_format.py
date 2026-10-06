"""
*`@file`* `_dt/_format.py`
"""
from __future__ import annotations
from datetime import date, datetime
from lute import LogMsg
from typing import (Literal)
from .. import (_array as Array, _string as String)

class FormatCode(String.BaseEnum):
    MONTH_NAME = "%B"
    MONTH_ABBR = "%b" # or %h ?
    MONTH_NUM = "%m"
    """ 0-padded """

    YEAR_FULL = "%Y"
    YEAR_ABBR = "%y"
    WEEK_NUM = "%V"
    """ 0-padded `01-53` """
    WEEKDAY_FULL = "%A"
    WEEKDAY_ABBR = "%a"
    WEEKDAY_NUM = "%w"
    """ `0-6` """
    WEEKDAY_ISO = "%u"
    """ `1-7` """

    DAY_NUM = "%d"
    """ 0-padded """
    DAY_365 = "%j"
    """ 0-padded `001-366` """

    HOUR_24 = "%H"
    HOUR_12 = "%I"
    MERIDIAN = "%p"
    UTC_OFFSET = "%z"
    UTC_ABBR = "%Z"

    MINUTE = "%M"
    SECOND = "%S"
    MICROSECOND = "%f"

    LOCALE_DATETIME = "%c"
    LOCALE_DATE = "%x"
    LOCALE_TIME = "%X"

    DATE_MDY = "%D"
    """ = `%m/%d/%y` """
    DATE_YMD = "%F"
    """ = `%Y-%m-%d` """

    TIME_24_HM = "%R"
    TIME_24_HMS = "%T"
    """ Time in 24-hour notation format `%H:%M:%S` """
    TIME_12 = "%r"

DateFormatCode = FormatCode

class FormatString(String.BaseEnum):
    YMD_HYPHEN = "%Y-%m-%d" # Code.DATE_YMD.value
    YMD_DOT = "%Y.%m.%d"
    YMD_NONE = "%Y%m%d"
    YMD_TIME_HYPHEN = "%Y-%m-%d %H:%M:%S"

    DT_STAMP = "%Y%m%dT%H%M%S"

    MDY_SLASH = "%m/%d/%Y" # Code.DATE_MDY.value
    MDY_DOT = "%m.%d.%Y"
    MDY_TIME_MERIDIAN_SLASH = "%m/%d/%Y %I:%M:%S %p"

    MY_SLASH ="%m/%Y"

    @staticmethod
    def ymd(
        date_sep: str | Literal['-', '.', '/']="-", 
        # part_sep: str | Literal['T', ' ']='T', 
        # time_sep: str | Literal['.', ':', '-']="."
    ):
        s = FormatCode.DATE_YMD.value
        if (date_sep != "-"):
            s = s.replace('-', date_sep)
        return s

DateFormatString = FormatString

def resolve_date_code(
    ref_date: date | datetime,
    *code: str | FormatCode
) -> dict[str, str]:
    """
    *`@returns`* `{ c: ref_date.strftime(c) for c in code }`
    """
    def _format(acc: dict[str, str], curr, _: int):
        acc[curr] = ref_date.strftime(curr)
        return acc
    try:
        return Array.reduce(code, _format, dict())
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            error=e, 
            ref_date=str(ref_date), 
            codes=str(code)
        )) from e

FORMAT_STRINGS = set(FormatString.values()).union(set(FormatCode.values()))

def can_format(s: str, /) -> bool:
    """
    *`@returns`* `s in FORMAT_STRINGS or String.contains(s, FormatCode.values(), ignore_case=False)`
    = whether `<date|datetime|time>.strftime(s) will change s` """
    return (
        s in FORMAT_STRINGS 
        or String.contains(s, FormatCode.values(), ignore_case=False)
    )

def resolve_optional_date_code(
    ref: date | datetime,
    s: str | FormatCode,
    /,
) -> str:
    """ 
    *`@returns`* `ref_date.strftime(s)`
    """
    return ref.strftime(s)

def matches_format(s: str, /, fmt: str | FormatString) -> bool: 
    try: # , cls: type[datetime] | type[date] | type[time]=datetime
        return isinstance(datetime.strptime(s, fmt), datetime)
    except Exception:
        return False
