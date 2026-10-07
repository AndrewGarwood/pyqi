"""
*`@file`* `models/_retry`
"""
from dataclasses import dataclass
from ..validation import require


@dataclass
class RetryOptions:
    """
    ```
    timeout: float = 120.0 # require positive number
    delay: float = 5.0 # require positive number
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

__all__ = ["RetryOptions"]