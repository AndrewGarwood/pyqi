"""
*`@file`* `io/_csv`
"""

from ._enum import BaseStrEnum
from ..fs._path import StrPath, to_path

class Delimiter(BaseStrEnum):
    """
    enum for common delimiter characters
    ```
    TAB = "\\t"
    NEW_LINE = "\\n"
    COMMA = ","
    PIPE = "|"
    SEMICOLON = ";"
    COLON = ":"
    ```
    """
    TAB = "\t"
    NEW_LINE = "\n"
    COMMA = ","
    PIPE = "|"
    SEMICOLON = ";"
    COLON = ":"

def get_header_length(
    path: StrPath, 
    /, 
    encoding: str = "utf-8", 
    delimiter: str | Delimiter = "\t"
) -> int:
    """ 
    *`@returns`* `num_cols: int` = `0 if not header else len(header.split(delimiter))`
    """
    with to_path(path).open("r", encoding=encoding) as f:
        header = f.readline().rstrip("\r\n")
        if not header:
            return 0
        ncols = len(header.split(delimiter))
        return ncols