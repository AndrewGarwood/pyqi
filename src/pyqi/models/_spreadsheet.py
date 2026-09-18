"""
*`@file`* `io/models/_spreadsheet`
"""

from ._enum import (MetaEnum)
from dataclasses import dataclass
from typing import (Optional)


@dataclass(frozen=True)
class SpreadsheetMeta:
    is_excel: bool
    separator: Optional[str] = None
    encoding: Optional[str] = None

# (python 3.11.13)
# pylance error: MetaEnum[str, SpreadsheetMeta] # Argument to class must be a base class
class SpreadsheetFileExt(MetaEnum):
    _value_: str
    meta: SpreadsheetMeta
    """
    ```   
    ext = SpreadsheetFileExt(".tsv")
    print(f"{ext=}")                 # <SpreadsheetFileExt.TSV: '.tsv'>
    print(f"{ext.value=}")           # ".tsv"
    print(f"{ext.separator=}")       # "\\t"
    print(f"{ext.is_excel=}")        # False
    ```
    """
    XLSX = (".xlsx", SpreadsheetMeta(is_excel=True))
    XLS = (".xls", SpreadsheetMeta(is_excel=True))
    XLSB = (".xlsb", SpreadsheetMeta(is_excel=True))
    XLSM = (".xlsm", SpreadsheetMeta(is_excel=True))
    CSV = (".csv", SpreadsheetMeta(is_excel=False, separator=","))
    TSV = (".tsv", SpreadsheetMeta(is_excel=False, separator="\t"))

    @property
    def separator(self) -> Optional[str]:
        return self.meta.separator

    @property
    def is_excel(self) -> bool:
        return self.meta.is_excel