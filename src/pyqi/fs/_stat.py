"""
*`@file`* `fs/_stat.py`
"""
from ._path import (StrPath, to_path)
from .types import SizeUnit
from lute import LogMsg



def format_bytestr(num_bytes: int, /) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    size = float(num_bytes)
    for unit in SizeUnit.values():
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size = size / 1024.0
    raise RuntimeError(f"{format_bytestr.__name__} Unreachable")

def size_of_file(path: StrPath, /) -> int:
    return to_path(path).stat().st_size


def size_of_dir(dir: StrPath, /) -> int:
    try:
        dir = to_path(dir)
        if (not dir.is_dir()): 
            raise ValueError(f"Provided path is not a directory")
        return sum(
            p.stat().st_size
            for p in dir.rglob("*")
            if p.is_file()
        )
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e,
            f"Faild to compute size of directory content",
            dir=str(dir)
        )) from e



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
