"""
*`@file`* `fs/types.py`
"""
from pathlib import Path
from typing import TypeAlias, Sequence, Literal

StrPath: TypeAlias = str | Path
DataExt: TypeAlias = Literal[".json", ".parquet", ".tsv", ".txt", ".csv", ".xlsx"] | str
TargetExt: TypeAlias = DataExt | Sequence[DataExt]
PathInput: TypeAlias = StrPath | Sequence[StrPath]