"""
*`@module`* `fs/__init__.py`
"""

from .types import *
from ._path import *
from ._dir import *
from ._file import *
from ._stat import *
from ._process import *
from ._rename import *
from ._search import *

from . import (
    _dir as directory,
    _file as file,
    _path as path,
    _stat as stat,
    _process as process,
    _rename as rename_tool,
    _search as search,
)
# def count_lines(filepath: Path) -> int:
#     """ includes header row """
#     with filepath.open("r", encoding="utf-8", errors="ignore") as f:
#         return sum(1 for _ in f)


# def count_line_terminators(filepath: Path) -> int:
#     """
#     - includes header row
#     - might return a number off by 1 if last row doesn't have a new line terminator
#     """
#     count = 0
#     with filepath.open("rb") as f:
#         for chunk in iter(lambda: f.read(8182), b""):
#             count+= chunk.count(b"\n")
#     return count