"""
*`@file`* `models/_result`
"""

from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass
from typing import (Generic, Optional, TypeVar, Any)
from lute import LogMsg
from ..utils import (export, HasDunderName, safe)

T = TypeVar("T")

class Result(Generic[T]):
    """
    `Result(Generic[T])`
    ```
    success: bool
    message: Optional[str]
    data: Optional[T]
    error: Optional[Exception | object]=None
    ```
    """
    source: str
    success: bool
    message: Optional[str]
    data: Optional[T]
    error: Optional[BaseException | object]=None
    def __init__(self, 
        source: Optional[str | HasDunderName]=None,
        data: Optional[T]=None, 
        success: Optional[bool]=None, 
        message: Optional[str | LogMsg]=None, 
        error: Optional[BaseException | object]=None,
        **kwargs
    ):
        self.source = (
            source if isinstance(source, str) 
            else source.__name__ if source 
            else "[Result]"
        )
        self.success = (
            success if isinstance(success, bool) 
            else (
                True 
                if (data is not None) and not bool(error) 
                else False
            )
        )
        self.message = (
            None if message is None or isinstance(message, str) 
            else message._format()
        )
        # self._result_timestamp = datetime.now()
        self.data = data
        self.error = error
        self.kwargs = kwargs

    def to_dict(self) -> dict[str, Any]:
        _data = (
            safe.invoke_method(self.data, "__dict__") 
            if self.data and hasattr(self.data, "__dict__") 
            else None
        )
        return {
            "source": self.source,
            # "timestamp": self._result_timestamp.isoformat(),
            "success": self.success,
            "message": self.message,
            "data": _data,
            "error": str(self.error) if self.error else None
        }
    
    @classmethod
    def ok(cls, 
        source: str | HasDunderName,
        /, 
        data: Optional[T] = None,
        message: Optional[str | LogMsg] = None,
    ) -> Result[T]:
        return cls(source, success=True, message=message, data=data, error=None)

    @classmethod
    def fail(
        cls,
        source: str | HasDunderName, 
        /,
        message: Optional[str | LogMsg] = None,
        error: Optional[Exception] = None,
        data: Optional[T] = None,
    ) -> Result[T]:
        
        return cls(source, success=False, message=message, data=data, error=error)


__all__ = export(Result)