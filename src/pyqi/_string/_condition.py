"""
*`@file`* `_string/condition`
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import (Any, Literal, Protocol, Self, TypedDict, Required, Callable, TypeGuard)
from lute import LogMsg
from ..types import Arbitrary, resolve_arbitrary
from .._json._serial import Serial
from .._function._partial import Partial
from ..models._enum import BaseStrEnum
from ..models._registry import CallableRegistry
from ._input import (StrInput)
import re

class StringCondition(BaseStrEnum):
    """ aka `StringPredicate` """
    CONTAINS = "CONTAINS"
    IS_EQUAL_TO = "IS_EQUAL_TO"
    EQUALS = "EQUALS" # alias for backwards compatibility
    ENDS_WITH = "ENDS_WITH"
    STARTS_WITH = "STARTS_WITH"
    MATCHES = "MATCHES"

    DOES_NOT_CONTAIN = "DOES_NOT_CONTAIN"
    IS_NOT_EQUAL_TO = "IS_NOT_EQUAL_TO"
    NOT_EQUALS = "NOT_EQUALS"
    DOES_NOT_END_WITH = "DOES_NOT_END_WITH"
    DOES_NOT_START_WITH = "DOES_NOT_START_WITH"
    DOES_NOT_MATCH = "DOES_NOT_MATCH"



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

@STRING_CONDITION_REGISTRY.register(StringCondition.DOES_NOT_CONTAIN)
def _not_contains(s: str, /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    """ 
    - *`@param`* `require_all` is vestigal (only present b/c of protocol) 
    - *`@returns`* `bool` whether `s` does not contain any of `target`
    """
    return not _contains(s, target, ignore_case, require_all=False)

@STRING_CONDITION_REGISTRY.register(StringCondition.IS_EQUAL_TO)
def _equals(s: str,  /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    """
    - *`@param`* `require_all` is vestigal
    - *`@returns`* `bool` whether `s` equals any of `target`
    """
    target = resolve_arbitrary(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    generator = (s == t for t in target)
    return any(generator)

@STRING_CONDITION_REGISTRY.register(StringCondition.IS_NOT_EQUAL_TO)
def _not_equals(s: str, /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    """
    - *`@param`* `require_all` is vestigal
    - *`@returns`* `bool` whether `s` is not equal to any of `target`
    """
    return not _equals(s, target, ignore_case, require_all=False)

@STRING_CONDITION_REGISTRY.register(StringCondition.ENDS_WITH)
def _endswith(s: str, /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    """
    - *`@param`* `require_all` is vestigal
    - *`@returns`* `bool` whether `s` ends with any of `target`
    """
    target = resolve_arbitrary(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return any(s.endswith(t) for t in target)

@STRING_CONDITION_REGISTRY.register(StringCondition.DOES_NOT_END_WITH)
def _not_endswith(s: str, /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    """
    - *`@param`* `require_all` is vestigal
    - *`@returns`* `bool` whether `s` does not end with any of `target`
    """
    return not _endswith(s, target, ignore_case, require_all=False)


@STRING_CONDITION_REGISTRY.register(StringCondition.STARTS_WITH)
def _startswith(s: str, /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    """
    - *`@param`* `require_all` is vestigal
    - *`@returns`* `bool` whether `s` starts with any of `target`
    """
    target = resolve_arbitrary(target)
    if ignore_case:
        s = s.casefold()
        target = tuple(t.casefold() for t in target)
    return any(s.startswith(t) for t in target)

@STRING_CONDITION_REGISTRY.register(StringCondition.DOES_NOT_START_WITH)
def _not_startswith(s: str, /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    """
    - *`@param`* `require_all` is vestigal
    - *`@returns`* `bool` whether `s` does not start with any of `target`
    """
    return not _startswith(s, target, ignore_case, require_all=False)

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

@STRING_CONDITION_REGISTRY.register(StringCondition.DOES_NOT_MATCH)
def _not_matches(
    s: str, 
    /, 
    target: Arbitrary[str | re.Pattern[str]], 
    ignore_case: bool=True, 
    require_all: bool=False
) -> bool:
    """
    - *`@param`* `require_all` is vestigal
    - *`@returns`* `bool` whether `s` does not match any of `target`
    """
    return not _matches(s, target, ignore_case, require_all=False)


# =============================================================================
# register enum values with identical meaning
# =============================================================================
STRING_CONDITION_REGISTRY.register(StringCondition.EQUALS)(_equals)
STRING_CONDITION_REGISTRY.register(StringCondition.NOT_EQUALS)(_not_equals)

# =============================================================================
# function aliases for better type hints
# =============================================================================
def contains(s: str,  /, target: StrInput, ignore_case: bool=True, require_all: bool=False) -> bool:
    return _contains(s, target, ignore_case, require_all)

def not_contains(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    return _not_contains(s, target, ignore_case)


def equals(s: str,  /, target: StrInput, ignore_case: bool=True) -> bool:
    return _equals(s, target, ignore_case)

def not_equals(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    return _not_equals(s, target, ignore_case)


def endswith(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    return _endswith(s, target, ignore_case)

def not_endswith(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    return _not_endswith(s, target, ignore_case)


def startswith(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    return _startswith(s, target, ignore_case)

def not_startswith(s: str, /, target: StrInput, ignore_case: bool=True) -> bool:
    return _not_startswith(s, target, ignore_case)

def matches(
    s: str, 
    /,
    target: Arbitrary[str | re.Pattern[str]], 
    ignore_case: bool=True, 
    require_all: bool=False,
) -> bool:
    return _matches(s, target, ignore_case, require_all)

def not_matches(
    s: str, 
    /, 
    target: Arbitrary[str | re.Pattern[str]], 
    ignore_case: bool=True
) -> bool:
    return _not_matches(s, target, ignore_case)


class StringConditionOptionsDict(TypedDict, total=False):
    condition: Required[str | StringCondition]
    target: Required[StrInput]
    ignore_case: bool
    require_all: bool

@dataclass
class StringConditionOptions(Serial[StringConditionOptionsDict]):
    condition: StringCondition
    ignore_case: bool = True
    require_all: bool = False
    def __init__(
        self,
        condition: StringCondition,
        target: StrInput,
        ignore_case: bool=True,
        require_all: bool=False
    ):
        self.condition = condition
        self._target = target
        self.ignore_case = ignore_case
        self.require_all = require_all

    @property
    def target(self):
        return resolve_arbitrary(self._target)
    
    @target.setter
    def target(self, other: StrInput, /):
        self._target = other
    
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


__all__ = [
    "STRING_CONDITION_REGISTRY", 
    "contains", "equals", "endswith", "startswith", "matches", 
    "not_contains", "not_equals", "not_endswith", "not_startswith", "not_matches",
    "StringCondition",
    "StringConditionOptions", 
    "StringConditionOptionsDict", 
    "compile_condition_options",
]