"""
*`@file`* `./_dt/constants.py`
"""

from __future__ import annotations
from typing import (TypeAlias)
import datetime as dt
from ..models._enum import BaseIntEnum

DateValue: TypeAlias = dt.date | dt.datetime | str

class Weekday(BaseIntEnum):
    """ 
    0-based index, `Monday=0`, . . . , `Sunday=6` 
    - to match `datetime.weekday()`
    
    """
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
