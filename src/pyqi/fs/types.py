"""
*`@file`* `fs/types.py`
"""
from pathlib import Path
from typing import TypeAlias, Sequence, Literal
from .._string._enum import BaseStrEnum
from enum import auto

StrPath: TypeAlias = str | Path
DataExt: TypeAlias = (Literal[
    ".json", 
    ".parquet", 
    ".tsv", 
    ".txt", 
    ".csv", 
    ".xlsx"
    ] 
    | str
)
TargetExt: TypeAlias = DataExt | Sequence[DataExt]
PathInput: TypeAlias = StrPath | Sequence[StrPath]


class RenameOperation(BaseStrEnum):
    PREPEND = auto()
    APPEND = auto()
    REPLACE = auto()

class ArchiveFormat(BaseStrEnum):
    """
    ```
    ZIP = ".zip"
    TAR = ".tar"
    TAR_GZ = ".tar.gz"
    TGZ = ".tgz"
    TAR_BZ2 = ".tar.bz2"
    TAR_XZ = ".tar.xz"
    GZ = ".gz" # (single file)
    BZ2 = ".bz2" # (single file)
    XZ = ".xz" # (single file)
    ```
    """
    ZIP = ".zip"
    TAR = ".tar"
    TAR_GZ = ".tar.gz"
    TGZ = ".tgz"
    TAR_BZ2 = ".tar.bz2"
    TAR_XZ = ".tar.xz"
    GZ = ".gz" # (single file)
    BZ2 = ".bz2" # (single file)
    XZ = ".xz" # (single file)


class SizeUnit(BaseStrEnum):
    BYTE = "B"
    KILOBYTE = "KB"
    MEGABYTE = "MB"
    GIGABYTE = "GB"
    TERRABYTE = "TB"

__all__ = [
    "StrPath", "DataExt", "TargetExt", "PathInput",
    "RenameOperation", "ArchiveFormat", "SizeUnit"
]