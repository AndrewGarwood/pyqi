"""
*`@file`* `_string/condition`
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import (Any, Literal, Protocol, Self, TypedDict, Required, Callable)
from lute import LogMsg
from ..types import Arbitrary, resolve_arbitrary
from .._json._serial import Serial
from .._function._partial import Partial
from ..models._enum import BaseStrEnum
from ..models._registry import Registry, TypedRegistry, CallableRegistry
from ._input import (StrInput)
import re

class StringCondition(BaseStrEnum):
    """ aka `StringPredicate` """
    CONTAINS = "CONTAINS"
    EQUALS = "EQUALS"
    ENDS_WITH = "ENDS_WITH"
    STARTS_WITH = "STARTS_WITH"
    MATCHES = "MATCHES"

class StringPredicate(Protocol):
    """
    `Protocol` `(target: StrInput | Any, ignore_case: bool = True, require_all: bool = False) -> bool`
    """
    def __call__(
        self,
        value: str,
        /,
        target: StrInput | Any,
        ignore_case: bool = True,
        require_all: bool = False,
    ) -> bool: ...

STRING_CONDITION_REGISTRY: CallableRegistry[
    StringCondition,
    StringPredicate,
] = CallableRegistry(
    StringCondition,
    normalize_key=StringCondition.resolve,
    name="StringConditionRegistry",
)

@STRING_CONDITION_REGISTRY.register(StringCondition.CONTAINS)
def _contains(
    s: str, 
    /, 
    target: StrInput, 
    ignore_case: bool=True, 
    require_all: bool=False,
) -> bool:
    target = resolve_arbitrary(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    generator = (t in s for t in target)
    return (
        any(generator) if not require_all 
        else all(generator)
    )

@STRING_CONDITION_REGISTRY.register(StringCondition.EQUALS)
def _equals(s: str,  /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    target = resolve_arbitrary(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    generator = (s == t for t in target)
    return any(generator)


@STRING_CONDITION_REGISTRY.register(StringCondition.ENDS_WITH)
def _endswith(s: str, /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    target = resolve_arbitrary(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return any(s.endswith(t) for t in target)


@STRING_CONDITION_REGISTRY.register(StringCondition.STARTS_WITH)
def _startswith(s: str, /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    target = resolve_arbitrary(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return any(s.startswith(t) for t in target)


@STRING_CONDITION_REGISTRY.register(StringCondition.MATCHES)
def _matches(
    s: str, 
    /, 
    target: Arbitrary[str | re.Pattern[str]], 
    ignore_case: bool=True, 
    require_all: bool=False,
) -> bool:
    _resolved_target_value = resolve_arbitrary(target)
    _resolved_pats: list[re.Pattern[str]] = []
    for x in _resolved_target_value:
        if (isinstance(x, str)):
            if (ignore_case):
                _resolved_pats.append(re.compile(x, re.IGNORECASE))
            else:
                _resolved_pats.append(re.compile(x))
        else:
            _resolved_pats.append(x)
    generator = (bool(re.match(pat, s)) for pat in _resolved_pats)
    return (
        all(generator) if require_all 
        else any(generator)
    )


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
    def from_dict(cls, data: StringConditionOptionsDict | dict[str, Any], /) -> Self:
        try:
            return cls(
                condition=StringCondition.resolve(data["condition"]),
                target=data['target'],
                ignore_case=data.get('ignore_case', True),
                require_all=data.get('require_all', False)
            )
        except (ValueError, KeyError): raise
        except Exception as e:
            raise RuntimeError(LogMsg.err(
                e,
                expected=StringConditionOptionsDict.__name__,
                received=str(data)
            )) from e

    @property
    def case_sensitive(self) -> bool:
        return not self.ignore_case


def compile_condition_options(o: StringConditionOptions | StringConditionOptionsDict, /): 
    if isinstance(o, dict): o = StringConditionOptions.from_dict(o)
    base_fn = STRING_CONDITION_REGISTRY.get(o.condition)
    return Partial(
        base_fn, 
        o.target, 
        o.ignore_case, 
        o.require_all
    )



# =============================================================================
# aliases for better type hints
# =============================================================================
def contains(s: str,  /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    return _contains(s, target, ignore_case, require_all, *[])

def equals(s: str,  /, target: StrInput, ignore_case: bool=True) -> bool:
    return _equals(s, target, ignore_case, *[])

def endswith(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    return _endswith(s, target, ignore_case, *[])

def startswith(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    return _startswith(s, target, ignore_case, *[])

def matches(
    s: str, 
    /,
    target: Arbitrary[str | re.Pattern[str]], 
    ignore_case: bool=True, 
    require_all: bool=False,
) -> bool:
    return _matches(s, target, ignore_case, require_all)

__all__ = [
    "STRING_CONDITION_REGISTRY", 
    "contains", "equals", "endswith", "startswith", "matches", "StringCondition",
    "StringConditionOptions", "StringConditionOptionsDict", "compile_condition_options"
]