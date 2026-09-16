"""
*`@file`* `<module>/models/_json/types.py`
"""
from __future__ import annotations
import json
from pathlib import Path
from abc import ABC, abstractmethod
from enum import Enum
from typing import (TypeVar, Protocol, TypeAlias, Any, Self, Generic, Mapping)

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = (
    JsonScalar
    | list["JsonValue"]
    | dict[str, "JsonValue"]
)
""" `= JsonScalar | list[JsonValue] | dict[str, JsonValue]` """
JsonObject: TypeAlias = dict[str, JsonValue]
""" `= dict[str, JsonValue]` """
