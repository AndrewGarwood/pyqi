

from __future__ import annotations
from ._enum import BaseStrEnum
from ._input import (StrInput, resolve_str_input, ResolvedStrInput)
from typing import (Generic, ParamSpec, TypeVar, Callable, TypeAlias)
from lute import LogMsg
import re

P = ParamSpec('P')
R = TypeVar('R')


CONDITION_OPERATOR_REGISTRY: dict[ConditionOperator, Callable[..., bool]] = {}

class ConditionOperator(BaseStrEnum):
    CONTAINS = "CONTAINS"
    EQUALS = "EQUALS"
    ENDS_WITH = "ENDS_WITH"
    STARTS_WITH = "STARTS_WITH"
    MATCHES = "MATCHES"


def get_condition_fn(name: ConditionOperator | str, /) -> Callable[[str], bool]:
    name = str(name).upper()
    keys = ConditionOperator.keys()
    if name not in keys:
        raise KeyError(LogMsg(
            f"Invalid key for ConditionOperator()",
            expected=f"one of {keys}",
            received=str(name)
        ))
    return CONDITION_OPERATOR_REGISTRY[ConditionOperator.get(name)]

def register_operator(name: ConditionOperator, /):
    def wrapper(fn: Callable[..., bool]):
        if name in CONDITION_OPERATOR_REGISTRY:
            raise ValueError(LogMsg(
                f"{name} already registered",
                existing_registry_value=getattr(CONDITION_OPERATOR_REGISTRY[name], "__name__", "<not available>"),
                proposed_registry_value=getattr(fn, "__name__", "<not available>")
            ))
        CONDITION_OPERATOR_REGISTRY[name] = fn
        return fn
    return wrapper

@register_operator(ConditionOperator.CONTAINS)
def _contains(s: str,  /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    target = resolve_str_input(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return (
        any(t in s for t in target) 
        if not require_all 
        else all(t in s for t in target)
    )

@register_operator(ConditionOperator.EQUALS)
def _equals(s: str,  /, target: StrInput, ignore_case: bool=True) -> bool:
    target = resolve_str_input(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return any(s == t for t in target)


@register_operator(ConditionOperator.ENDS_WITH)
def _endswith(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    target = resolve_str_input(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return any(s.endswith(t) for t in target)


@register_operator(ConditionOperator.STARTS_WITH)
def _startswith(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    target = resolve_str_input(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return any(s.startswith(t) for t in target)


@register_operator(ConditionOperator.MATCHES)
def _matches(s: str, /, target: str | re.Pattern[str]) -> bool:
    pat = (
        target if isinstance(target, re.Pattern) 
        else re.compile(target) # re.compile(rf"(?<=.){target}(?=.)")
    )
    return bool(re.match(pat, s)) # pat.search(s)



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
