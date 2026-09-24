"""
*`@file`* `_utils`
"""
from typing import Protocol, Iterable

class HasDunderName(Protocol):
    @property
    def __name__(self) -> str: ...

def export_symbols(
    *items: HasDunderName, 
) -> tuple[str, ...]:
    return tuple(x.__name__ for x in items)
