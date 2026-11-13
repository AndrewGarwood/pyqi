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
"""
` = ['January', 'February', 'March', 'April', 'May', 
'June', 'July', 'August', 'September', 'October', 'November', 'December'
]`
- `"%B"`
"""

MONTH_ABBREVS = list(calendar.month_abbr[1:])
"""
`= [
'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 
'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]`
- `"%b"`
"""

EXCEL_EPOCH = dt.datetime(1899, 12, 30)
""" Excel's default Windows date system is: `1899-12-30` """

EXCEL_1904_EPOCH = dt.datetime(1904, 1, 1)
"""
alternate date system for excel workbooks
[Workbook.Date1904 property (Excel)](https://learn.microsoft.com/en-us/office/vba/api/excel.workbook.date1904)
"""

__all__ = [
    "Weekday",
    "MONTH_NAMES",
    "MONTH_ABBREVS",
    "EXCEL_EPOCH",
    "EXCEL_1904_EPOCH"
]