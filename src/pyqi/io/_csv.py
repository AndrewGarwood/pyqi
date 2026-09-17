"""
*`@file`* `io/_csv`
"""

from .._string import BaseStrEnum


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
