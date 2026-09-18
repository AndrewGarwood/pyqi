"""
*`@file`* `_array/matrix`
- TODO: choose better name for file
"""

from typing import (Any, Sequence, Optional)
from . import functions as _Array



def standardize_row_length(
    rows: Sequence[Sequence[Any]],
    /,
    num_cols: Optional[int]=None,
    fill_value: Optional[Any]=None
) -> list[list[Any]]:
    """ i.e. return arr with len all subarrays = `N` """
    if not rows:
        return []
    num_cols = max(_Array.map(rows, len)) if num_cols is None else num_cols
    result: list[list[Any]] = []
    for r in rows:
        row = list(r)
        if len(row) > num_cols:
            row = row[:num_cols]
        elif len(row) < num_cols:
            row.extend([fill_value] * (num_cols - len(row)))
        result.append(row)
    return result