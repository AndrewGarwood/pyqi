"""
*`@file`* `_json/serial.py`
"""
from __future__ import annotations
import json
from pathlib import Path
from abc import ABC, abstractmethod
from enum import Enum
from typing import (TypeVar, Protocol, TypeAlias, Any, Self, Generic, Mapping)
from .types import (JsonObject, JsonScalar, JsonValue)


class DataModelError(ValueError):
    """Raised when model deserialization or serialization fails."""


class SerializableDataClass(ABC):
    @classmethod
    @abstractmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
        /,
    ) -> Self:
        """Construct an instance from mapping data."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> JsonObject:
        """Return a JSON-compatible dictionary."""
        raise NotImplementedError

    @classmethod
    def from_json(cls, source: str | bytes | Path, /) -> Self:
        """
        Construct an instance from a JSON string, bytes, or file path.

        Path objects are always interpreted as files. Strings are interpreted
        as JSON text to avoid guessing whether arbitrary text is a path.
        """
        try:
            if isinstance(source, Path):
                with source.open(
                    mode="r",
                    encoding="utf-8",
                ) as file:
                    data = json.load(file)
            else:
                data = json.loads(source)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise DataModelError(
                f"Could not load {cls.__name__} JSON from {type(source)=}"
            ) from exc
        if not isinstance(data, dict):
            raise DataModelError(
                f"{cls.__name__} requires a JSON object; "
                f"received {type(data).__name__}"
            )

        return cls.from_dict(data)

    @classmethod
    def from_json_file(
        cls,
        path: str | Path,
        /,
    ) -> Self:
        return cls.from_json(Path(path))

    def to_json(
        self,
        *,
        indent: int | None = 2,
        sort_keys: bool = False,
    ) -> str:
        try:
            return json.dumps(
                self.to_dict(),
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=False,
            )
        except (TypeError, ValueError) as exc:
            raise DataModelError(
                f"Could not serialize {type(self).__name__}"
            ) from exc

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
        except (OSError, TypeError, ValueError) as exc:
            raise DataModelError(
                f"Could not write {type(self).__name__} "
                f"to {resolved_path}"
            ) from exc
