"""
*`@file`* `models/_enum`
"""
from __future__ import annotations
from functools import cached_property, cache
from enum import (Enum, StrEnum, IntEnum)
from typing import (Any, Generic, TypeVar, Self, TypeGuard)
from lute import LogMsg, annotate



# ============================================================================
# Enum with metadata
# ============================================================================
ValueT = TypeVar("ValueT", bound=(str | int))
""" `constraints: str, int` """
MetaT = TypeVar("MetaT") # , bound=object
# """ `constraints: object` """

class MetaEnum(Generic[ValueT, MetaT], Enum):
    """
    Base class for enums declared as:
    ```
    MEMBER = (value, metadata)
    ```
    - The first tuple element becomes the enum's canonical `.value`.
    - The second tuple element is exposed as `.meta`.
    """
    _value_: ValueT
    meta: MetaT
    def __new__(
        cls,
        value: ValueT,
        meta: MetaT,
    ) -> Self:
        member = object.__new__(cls)
        member._value_ = value
        member.meta = meta
        return member

    @classmethod
    def from_value(cls, value: ValueT, /,) -> Self:
        """ *`@returns`* `cls(value)` """
        return cls(value)

    @classmethod
    def try_from_value(
        cls,
        value: ValueT,
        /,
    ) -> Self | None:
        try: return cls(value)
        except ValueError: return None

    @classmethod
    def members(cls) -> tuple[Self, ...]:
        """ *`@returns`* `tuple(cls)` """
        return tuple(cls)
    
    @classmethod
    def names(cls) -> tuple[str, ...]:
        """ 
        *`@returns`* `tuple(m.name for m in cls)` 
        """
        return tuple(m.name for m in cls)

    @classmethod
    def keys(cls) -> tuple[str, ...]: 
        """ 
        *`@returns`* `tuple(m.name for m in cls)` 
        """
        return cls.names()

    @classmethod
    def contains(cls, key: str) -> bool:
        return key in cls.__members__

    @classmethod
    def values(cls):
        """ 
        *`@returns`* `tuple[ValueT, ...] = tuple(m.value for m in cls)` 
        """
        return tuple(m.value for m in cls)

    @classmethod
    def meta_values(cls):
        """ 
        *`@returns`* `tuple(m.meta for m in cls)` 
        """
        return tuple(m.meta for m in cls)

    @classmethod
    def items(cls):
        """ 
        *`@returns`* `tuple((m.name, m) for m in cls)` 
        - `len(cls.items()[i]) == 2`
        - `cls.items()[i][0] (str)` key/name
        - `cls.items()[i][1] (MetaEnum[ValueT, MetaT]) { value: ValueT; meta: MetaT }`
        """
        return tuple((m.name, m) for m in cls)

    @classmethod
    def value_items(cls) -> tuple[tuple[str, ValueT], ...]:
        """
        *`@returns`* `tuple((m.name, m.value) for m in cls)` 
        - `len(cls.value_items()[i]) == 2`
        - `cls.value_items()[i][0] (str)` = key/name
        - `cls.value_items()[i][1] (ValueT)` = canonical value
        """
        return tuple((m.name, m.value) for m in cls)
    
    @classmethod
    def full_items(cls) -> tuple[tuple[str, ValueT, MetaT], ...]:
        """
        *`@returns`* `tuple((m.name, m.value, m.meta) for m in cls)` 
        - `len(cls.full_items()[i]) == 3`
        - `cls.full_items()[i][0] (str)` = key/name
        - `cls.full_items()[i][1] (ValueT)` = canonical value
        - `cls.full_items()[i][2] (MetaT)` = metadata object
        """
        return tuple((m.name, m.value, m.meta) for m in cls)

    @classmethod
    def meta_items(cls) -> tuple[tuple[str, MetaT], ...]:
        """
        *`@returns`* `tuple((m.name, m.meta) for m in cls)` 
        - `len(cls.meta_items()[i]) == 2`
        - `cls.meta_items()[i][0] (str)` = key/name
        - `cls.meta_items()[i][1] (MetaT)` = metadata object
        """
        return tuple((m.name, m.meta) for m in cls)


"""
I'd prefer BaseStrEnum and BaseIntEnum both inherit from BaseEnum<ValueT>, 
but type hint no bueno. at least for 3.11
"""
class cached_classproperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if owner is None:
            return self
        # Compute the value using the class (owner)
        value = self.func(owner)
        # Cache the calculated value directly onto the class, overwriting the descriptor
        setattr(owner, self.func.__name__, value)
        return value
    
# ============================================================================
# StrEnum
# ============================================================================
class BaseStrEnum(StrEnum):
    """
    `name = <string>`
    - applies `@functools.cache` decorator 
    to class methods: `members, names, keys, values`
    """
    
    @classmethod
    @cache
    def members(cls) -> tuple[Self, ...]:
        """ 
        - *`@returns`* `tuple(cls)` 
        """
        return tuple(cls)
    
    @classmethod
    @cache
    def names(cls) -> tuple[str, ...]:
        """ 
        - *`@returns`* `tuple(m.name for m in cls)` 
        """
        return tuple(m.name for m in cls)

    @classmethod
    @cache
    def keys(cls) -> tuple[str, ...]: 
        """ 
        - *`@returns`* `tuple(m.name for m in cls)` 
        """
        return cls.names()

    @classmethod
    @cache
    def values(cls, unique: bool=True) -> tuple[str, ...]:
        """ 
        - *`@returns`* 
        `tuple(m.value for m in cls) if not unique 
        else tuple(set(m.value for m in cls))` 
        """
        return (
            tuple(m.value for m in cls) if not unique
            else tuple(set(m.value for m in cls))
        )

    @classmethod
    def get(cls, key: str, /) -> Self:
        """ *`@returns`* `cls[key]` """
        return cls[key]

    @classmethod
    def from_value(cls, value: str, /) -> Self:
        return cls(value)

    @classmethod
    def contains(cls, key: str, /) -> bool:
        """ 
        *`@returns`* `key in cls.__members__`
        - `type(cls.__members__)` = `MappingProxyType[str, BaseStrEnum*]*`
        """
        return key in cls.__members__

    @classmethod
    def resolve(cls, item: str | Self, /) -> Self:
        if (isinstance(item, cls)):
            return item
        try: 
            return cls.get(item)
        except Exception as ke:
            try: 
                return cls(item)
            except Exception as ve:
                raise RuntimeError(LogMsg(
                    f"Unable to resolve item to {cls.__name__}",
                    expected=f"cls | str (element of cls.keys() or cls.values())",
                    received=annotate(item),
                    key_error=annotate(ke),
                    value_error=annotate(ve)
                )) from ve

# ============================================================================
# IntEnum
# =============================================================================
class BaseIntEnum(IntEnum):
    """
    `name = <int>`
    - applies `@functools.cache` decorator 
    to class methods: `members, names, keys, values`
    """
    
    @classmethod
    @cache
    def members(cls) -> tuple[Self, ...]:
        """ 
        - *`@returns`* `tuple(cls)` 
        """
        return tuple(cls)
    
    @classmethod
    @cache
    def names(cls) -> tuple[str, ...]:
        """ 
        - *`@returns`* `tuple(m.name for m in cls)` 
        """
        return tuple(m.name for m in cls)

    @classmethod
    @cache
    def keys(cls) -> tuple[str, ...]: 
        """ 
        - *`@returns`* `tuple(m.name for m in cls)` 
        """
        return cls.names()

    @classmethod
    @cache
    def values(cls, unique: bool=True) -> tuple[int, ...]:
        """ 
        - *`@returns`* 
        `tuple(m.value for m in cls) if not unique 
        else tuple(set(m.value for m in cls))` 
        """
        return (
            tuple(m.value for m in cls) if not unique
            else tuple(set(m.value for m in cls))
        )

    @classmethod
    def get(cls, key: str, /) -> Self:
        """ *`@returns`* `cls[key]` """
        return cls[key]

    @classmethod
    def contains(cls, key: str, /) -> bool:
        """ *`@returns`* `key in cls.__members__` """
        return key in cls.__members__

    @classmethod
    def resolve(cls, item: str | int | Self, /) -> Self:
        if (isinstance(item, cls)): 
            return item
        try:
            return cls(item) if isinstance(item, int) else cls[item]
        except Exception as e:
            raise RuntimeError(LogMsg(
                f"Unable to resolve item to {cls.__name__}",
                expected=f"cls | str (element of self.keys()) | int (element of self.values())",
                received=annotate(item),
                error=annotate(e)
            )) from e
