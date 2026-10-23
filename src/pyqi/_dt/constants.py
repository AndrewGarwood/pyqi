"""
*`@file`* `./_dt/constants.py`
"""

from __future__ import annotations
import calendar
import datetime as dt
from ..models._enum import BaseIntEnum


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


MONTH_NAMES = list(calendar.month_name[1:])


EXCEL_EPOCH = dt.datetime(1899, 12, 30)
""" Excel's default Windows date system is: `1899-12-30` """
