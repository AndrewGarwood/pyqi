"""
*`@file`* `io/models/_spreadsheet`
"""

from ._enum import (MetaEnum)
from dataclasses import dataclass
from functools import cache
from ..utils import export
from lute import LogMsg

@dataclass(frozen=True)
class SpreadsheetMeta:
    is_excel: bool
    separator: str | None = None
    encoding: str | None = None
    
# (python 3.11.13)
# pylance error: MetaEnum[str, SpreadsheetMeta] # Argument to class must be a base class
class SpreadsheetFileExt(MetaEnum):
    """
    ```
    # (python 3.11.13) MetaEnum[str, SpreadsheetMeta] # pylance error: Argument to class must be a base class
    # temp solution
    _value_: str 
    meta: SpreadsheetMeta
    ```
    example
    ```   
    ext = SpreadsheetFileExt(".tsv")
    print(f"{ext=}")                 # <SpreadsheetFileExt.TSV: '.tsv'>
    print(f"{ext.value=}")           # ".tsv"
    print(f"{ext.separator=}")       # "\\t"
    print(f"{ext.is_excel=}")        # False
    ```
    """
    _value_: str
    meta: SpreadsheetMeta

    XLSX = (".xlsx", SpreadsheetMeta(is_excel=True))
    XLS = (".xls", SpreadsheetMeta(is_excel=True))
    XLSB = (".xlsb", SpreadsheetMeta(is_excel=True))
    XLSM = (".xlsm", SpreadsheetMeta(is_excel=True))
    CSV = (".csv", SpreadsheetMeta(is_excel=False, separator=","))
    TSV = (".tsv", SpreadsheetMeta(is_excel=False, separator="\t"))

    @property
    def separator(self) -> str:
        """
        *`@raises`* `ValueError` if `self.meta.separator` is undefined
        """
        if not self.meta.separator:
            raise ValueError(LogMsg(
                f"No separator is defined for this file extension.",
                self=str(self),
                self_meta=str(self.meta)
            ))
        return self.meta.separator

    @property
    def is_excel(self) -> bool:
        return self.meta.is_excel

    @classmethod
    @cache
    def excel_extensions(cls) -> list[str]:
        """
        *`@returns`* `list(v.value for v in cls.members() if v.meta.is_excel)`
        """
        return list(v.value for v in cls.members() if v.meta.is_excel)


__all__ = export(SpreadsheetMeta, SpreadsheetFileExt)