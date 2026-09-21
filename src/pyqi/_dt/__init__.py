"""
*`@module`* `_dt/__init__.py`
"""
from .constants import *
from ._format import *

from . import (
    _date as Date, 
    _datetime as Datetime,
    _minutes as Minutes,
    _seconds as Seconds
)

from ._date import (
    resolve as resolve_date,
    today
)
from ._datetime import (
    resolve_datetime as resolve_datetime, # for when rename to resolve in _datetime.py
    now
)
