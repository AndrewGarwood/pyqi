"""
*`@file`* `models/_result`
"""

from __future__ import annotations
from typing import (Generic, Optional, TypeVar, Any)
from lute import LogMsg
from ..utils import (export, HasDunderName, safe)
from json import dumps

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
    notes: list[Any]
    def __init__(self, 
        source: Optional[str | HasDunderName]=None,
        data: Optional[T]=None, 
        success: Optional[bool]=None, 
        message: Optional[str | LogMsg]=None, 
        error: Optional[BaseException | object]=None,
        # *notes,
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
        self.notes = []# list(notes)

    def add_note(self, *note: Any) -> None:
        for item in note:
            self.notes.append(item)
        # self.notes.append(note)

    def to_dict(self) -> dict[str, Any]:
        _data = (
        #     safe.invoke_method(self.data, "__dict__") 
        #     if self.data and hasattr(self.data, "__dict__") 
            safe.invoke_method(self.data, "to_dict") 
            if self.data and hasattr(self.data, "to_dict") 
            else str(self.data) if self.data 
            else None
        )
        return {
            "source": self.source,
            # "timestamp": self._result_timestamp.isoformat(),
            "success": self.success,
            "message": self.message,
            "data": _data,
            "error": str(self.error) if self.error else None,
            "notes": self.notes,
            "kwargs": self.kwargs
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<T>" + dumps(self.to_dict(), indent=4)
    
    @classmethod
    def ok(cls, 
        source: str | HasDunderName,
        /, 
        data: Optional[T] = None,
        message: Optional[str | LogMsg] = None,
        **kwargs
    ) -> Result[T]:
        return cls(
            source, 
            success=True, 
            message=message, 
            data=data, 
            error=None, 
            **kwargs
        )

    @classmethod
    def fail(
        cls,
        source: str | HasDunderName, 
        /,
        message: Optional[str | LogMsg] = None,
        error: Optional[Exception] = None,
        data: Optional[T] = None,
        **kwargs
    ) -> Result[T]:
        return cls(
            source, 
            success=False, 
            message=message, 
            data=data, 
            error=error, 
            **kwargs
        )


__all__ = export(Result)