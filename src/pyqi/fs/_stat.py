"""
*`@file`* `fs/_stat.py`
"""
from pathlib import Path
from ._file import size_of_file
from ._path import (StrPath, to_path)
from ._dir import (size_of_dir)
from lute import LogMsg
from .. import _string as String


class SizeUnit(String.BaseEnum):
    BYTE = "B"
    KILOBYTE = "KB"
    MEGABYTE = "MB"
    GIGABYTE = "GB"
    TERRABYTE = "TB"

def _format_bytestr(num_bytes: int, /) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    size = float(num_bytes)
    for unit in SizeUnit.values():
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size = size / 1024.0
    raise RuntimeError(f"{_format_bytestr.__name__} Unreachable")


def size_of(path: StrPath, /) -> int:
    try:
        path = to_path(path)
        return (
            size_of_dir(path) if path.is_dir() 
            else size_of_file(path)
        )
    except Exception as e:
        raise RuntimeError(LogMsg.err(e))

def get_stat(path: StrPath, /):
    return to_path(path).stat()
