"""
*`@file`* `fs/types.py`
"""
from pathlib import Path
from typing import TypeAlias, Sequence, Literal
from .._string._enum import BaseStrEnum
from enum import auto

StrPath: TypeAlias = str | Path
DataExt: TypeAlias = Literal[".json", ".parquet", ".tsv", ".txt", ".csv", ".xlsx"] | str
TargetExt: TypeAlias = DataExt | Sequence[DataExt]
PathInput: TypeAlias = StrPath | Sequence[StrPath]


class RenameOperation(BaseStrEnum):
    PREPEND = auto()
    APPEND = auto()
    REPLACE = auto()
