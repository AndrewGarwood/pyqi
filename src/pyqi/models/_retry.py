"""
*`@file`* `models/_retry`
"""
from dataclasses import dataclass
from typing import (Any, Self, TypedDict)
from .._utils import export
from .._json._serial import Serial
from ..validation import require

class RetryOptionsDict(TypedDict, total=False):
    timeout: float
    delay: float
    max_attempts: int

@dataclass(slots=True)
class RetryOptions(Serial[RetryOptionsDict]):
    """
    ```
    timeout: float = 120.0 # (seconds) require positive number
    delay: float = 5.0 # (seconds)require positive number
    max_attempts: int = 3 # require positive int
    ```
    """
    timeout: float
    delay: float
    max_attempts: int
    def __init__(self, 
        timeout: float = 120.0,
        delay: float = 5.0,
        max_attempts: int = 3,
    ):
        self.timeout = require.positive_number(timeout)
        self.delay = require.positive_number(delay)
        self.max_attempts = require.positive_integer(max_attempts)

    @classmethod
    def from_dict(cls, data: RetryOptionsDict | dict[str, Any]) -> Self:
        return cls(
            timeout=data.get('timeout', 120.0),
            delay=data.get('delay', 5.0),
            max_attempts=data.get('max_attempts', 3)
        ) 
    
__all__ = export(RetryOptionsDict, RetryOptions)