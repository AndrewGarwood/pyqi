

from __future__ import annotations
from ._enum import BaseStrEnum
from typing import (Generic, ParamSpec, TypeVar, Callable, TypeAlias)
from lute import LogMsg

P = ParamSpec('P')
R = TypeVar('R')


CONDITION_OPERATOR_REGISTRY: dict[ConditionOperator, Callable[[str], bool]] = {}

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
    def wrapper(fn: Callable[[str], bool]):
        if name in CONDITION_OPERATOR_REGISTRY:
            raise ValueError(LogMsg(
                f"{name} already registered",
                existing_registry_value=getattr(CONDITION_OPERATOR_REGISTRY[name], "__name__", "<not available>"),
                proposed_registry_value=getattr(fn, "__name__", "<not available>")
            ))
        CONDITION_OPERATOR_REGISTRY[name] = fn
        return fn
    return wrapper