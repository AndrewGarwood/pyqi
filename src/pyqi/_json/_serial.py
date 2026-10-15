"""
*`@file`* `_json/serial.py`
- TODO: should use pydantic
"""
from __future__ import annotations
import json
from datetime import date, datetime, time
from functools import cached_property
from pathlib import Path
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import (Any, TypeVar, Self, Generic, TypeGuard, Iterable)
# from pydantic import BaseModel
from lute import LogMsg
from .types import (JsonDict, JsonValue, is_json_value)
from ..types import is_primitive
from .. import _array as Array
from ..utils import export


T = TypeVar("T", bound=(Mapping))

def is_serializeable(value: Any, /) -> TypeGuard[JsonValue | Serial]:
    return (isinstance(value, Serial) or is_json_value(value))

def serialize(value: Any, /) -> JsonValue:
    # if (isinstance(value, Serial)): 
    #     return value.to_dict()
    if (is_primitive(value)):
        return value
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if (Array.isArray(value)):
        return Array.map(value, serialize)
    if (isinstance(value, Mapping)):
        return {
            k: serialize(v) 
            for k, v in value.items()
        }
    if (is_json_value(value)):
        return serialize(value)
    raise DataModelError(LogMsg(
        f"Unable to serialize value: {type(value).__name__=}"
    ))

class DataModelError(ValueError):
    """Raised when model deserialization or serialization fails."""


class Serial(ABC, Generic[T]):
    """
    `ABC, Generic[T],` 
    - where `T = TypeVar("T", bound=(Mapping))`
    - TODO: just use pydantic BaseModel ?
    ```
    - @abstractmethod def from_dict(cls, data: JsonDict[T],/)
    - def to_dict(self) -> JsonDict[T] # should overwrite

    - @classmethod def from_json(cls, ...)
    - @classmethod def from_json_file(cls, ...)
    
    - def to_json_string(self, ...)
    - def to_json_file(self, ...)
    
    - def keys(self) -> tuple[str,...]: ...
    - def items(self) -> tuple[tuple[str, Any | None], ...]: ...
    ```
    """
    def keys(self):
        """ 
        *`@returns`* `Array.filter(dir(self), lambda k: not _is_builtin_prop(k))`
        """
        return tuple(Array.filter(dir(self), lambda k: not _is_builtin_prop(k)))

    def items(self) -> tuple[tuple[str, Any | None], ...]:
        """ 
        *`@returns`* `Array.map(self.keys(), lambda k: (k, getattr(self, k, None)))`
        """
        return tuple(Array.map(self.keys(), lambda k: (k, getattr(self, k, None))))

    @classmethod
    @abstractmethod
    def from_dict(
        cls,
        data: JsonDict[T],
        /,
    ) -> Self:
        """`@abstract` Construct an instance from mapping data."""
        raise NotImplementedError
    
    def to_dict(self) -> JsonDict[T]:
        """Return a JSON-compatible dictionary."""
        # items = self.items()
        result: JsonDict[T] = dict()
        for k, v in self.items():
            try: result[k] = serialize(v)
            except Exception: pass
        return result

    @classmethod
    def from_json(cls, src: str | bytes | Path, /) -> Self:
        """
        Construct an instance from a JSON string, bytes, or file path.

        - `Path` objects are interpreted as files. 
        - `Strings` are interpreted as JSON text
        """
        try:
            if isinstance(src, Path):
                with src.open(
                    mode="r",
                    encoding="utf-8",
                ) as file:
                    data = json.load(file)
            else:
                data = json.loads(src)
        except (OSError, UnicodeError, json.JSONDecodeError) as e:
            raise DataModelError(LogMsg.err(e,
                f"Could not load {cls.__name__} JSON from {type(src)=}"
            )) from e
        if not isinstance(data, dict):
            raise DataModelError(LogMsg(
                f"{cls.__name__} requires a JSON object; "
                f"received {type(data).__name__}"
            ))
        return cls.from_dict(data)

    @classmethod
    def from_json_file(
        cls,
        path: str | Path,
        /,
    ) -> Self:
        return cls.from_json(Path(path))

    def to_json_string(
        self,
        *,
        indent: int | None = 4,
        sort_keys: bool = False,
    ) -> str:
        try:
            return json.dumps(
                self.to_dict(),
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=False,
            )
        except (TypeError, ValueError) as e:
            raise DataModelError(LogMsg.err(e,
                f"Could not serialize {type(self).__name__}"
            )) from e

    def to_json_file(
        self,
        path: str | Path,
        /,
        *,
        indent: int | None = 4,
        sort_keys: bool = False,
    ) -> None:
        resolved_path = Path(path)

        try:
            with resolved_path.open(
                mode="w",
                encoding="utf-8",
                newline="\n",
            ) as file:
                json.dump(
                    self.to_dict(),
                    file,
                    indent=indent,
                    sort_keys=sort_keys,
                    ensure_ascii=False,
                )
                file.write("\n")
        except (OSError, TypeError, ValueError) as e:
            raise DataModelError(LogMsg.err(e,
                f"Could not write {type(self).__name__} "
                f"to {resolved_path}",
            )) from e
        
    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__}>" 
            + json.dumps(self.to_dict(), indent=4)
        )

    def __repr__(self) -> str: return self.__str__()

    def __attr_label__(self, attr: str, /) -> str:
        """ 
        *`@returns`* `f"{self.__class__.__name__}.{attr}"`
        """
        return f"{self.__cls_name__}.{attr}"

    @cached_property
    def __cls_name__(self):
        return self.__class__.__name__

def _is_builtin_prop(value: str, /) -> bool:
    """
    *`@returns`* `(is_dunder_prop(value) or value in _PROPS_TO_IGNORE)`
    """
    return (is_dunder_prop(value) or value in _PROPS_TO_IGNORE)

_PROPS_TO_IGNORE: set[str] = set([
    '_is_protocol',
])

def is_dunder_prop(value: str, /) -> bool:
    return (
        len(value) > 4 
        and value.startswith("__") 
        and value.endswith("__")
    )

__all__ = export(Serial, serialize, is_serializeable, DataModelError)