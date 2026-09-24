"""
*`@file`* `validation/guard/_string`
"""


from typing import (Any, TypeGuard)

def is_non_empty_string(value: Any, /) -> TypeGuard[str]:
    return (isinstance(value, str) and bool(value.strip()))
