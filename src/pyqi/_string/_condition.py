"""
*`@file`* `_string/condition`
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import (Any, Self, TypedDict, Required)
from lute import LogMsg
from .._json import Serial
from ..models._enum import BaseStrEnum
from ..models._registry import Registry
from ._input import (StrInput, resolve_str_input)
import re

class StringCondition(BaseStrEnum):
    """ aka `StringPredicate` """
    CONTAINS = "CONTAINS"
    EQUALS = "EQUALS"
    ENDS_WITH = "ENDS_WITH"
    STARTS_WITH = "STARTS_WITH"
    MATCHES = "MATCHES"

STRING_CONDITION_REGISTRY: Registry[
    StringCondition, 
    bool
] = Registry(
    StringCondition, 
    StringCondition.resolve
)

@STRING_CONDITION_REGISTRY.register(StringCondition.CONTAINS)
def _contains(
    s: str, 
    /, 
    target: StrInput, 
    ignore_case: bool=True, 
    require_all: bool=False,
) -> bool:
    target = resolve_str_input(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return (
        any(t in s for t in target) 
        if not require_all 
        else all(t in s for t in target)
    )

@STRING_CONDITION_REGISTRY.register(StringCondition.EQUALS)
def _equals(s: str,  /, target: StrInput, ignore_case: bool=True, *args, **kwargs) -> bool:
    target = resolve_str_input(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return any(s == t for t in target)


@STRING_CONDITION_REGISTRY.register(StringCondition.ENDS_WITH)
def _endswith(s: str, /, target: StrInput, ignore_case: bool=True, *args, **kwargs) -> bool:
    target = resolve_str_input(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return any(s.endswith(t) for t in target)


@STRING_CONDITION_REGISTRY.register(StringCondition.STARTS_WITH)
def _startswith(s: str, /, target: StrInput, ignore_case: bool=True, *args, **kwargs) -> bool:
    target = resolve_str_input(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return any(s.startswith(t) for t in target)


@STRING_CONDITION_REGISTRY.register(StringCondition.MATCHES)
def _matches(s: str, /, target: str | re.Pattern[str], *args, **kwargs) -> bool:
    pat = (
        target if isinstance(target, re.Pattern) 
        else re.compile(target) # re.compile(rf"(?<=.){target}(?=.)")
    )
    return bool(re.match(pat, s)) # pat.search(s)


class StringConditionOptionsDict(TypedDict, total=False):
    condition: Required[str | StringCondition]
    target: Required[StrInput]
    ignore_case: bool
    require_all: bool

@dataclass
class StringConditionOptions(Serial[StringConditionOptionsDict]):
    condition: StringCondition
    target: StrInput
    ignore_case: bool = True
    require_all: bool = False

    @classmethod
    def from_dict(cls, data: StringConditionOptionsDict | dict[str, Any]) -> Self:
        try:
            return cls(
                condition=StringCondition.resolve(data["condition"]),
                target=data['target'],
                ignore_case=data.get('ignore_case', True),
                require_all=data.get('require_all', False)
            )
        except Exception as e:
            raise RuntimeError(LogMsg.err(
                e,
                expected=StringConditionOptionsDict.__name__,
                received=str(data)
            )) from e

    @property
    def case_sensitive(self) -> bool:
        return not self.ignore_case




# =============================================================================
# aliases for better type hints
# =============================================================================
def contains(s: str,  /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    return _contains(s, target, ignore_case=ignore_case, require_all=require_all)

def equals(s: str,  /, target: StrInput, ignore_case: bool=True) -> bool:
    return _equals(s, target, ignore_case=ignore_case)

def endswith(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    return _endswith(s, target, ignore_case=ignore_case)

def startswith(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    return _startswith(s, target, ignore_case=ignore_case)

def matches(s: str, target: str | re.Pattern[str]) -> bool:
    return _matches(s, target)

__all__ = [
    "STRING_CONDITION_REGISTRY", 
    "contains", "equals", "endswith", "startswith", "matches", 
    "StringConditionOptions", "StringConditionOptionsDict"
]