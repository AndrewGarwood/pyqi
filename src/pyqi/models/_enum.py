"""
*`@file`* `models/_enum`
"""
from __future__ import annotations
from enum import (Enum, StrEnum, IntEnum)
from typing import (Generic, TypeVar, Self)



# ============================================================================
# Enum with metadata
# ============================================================================
ValueT = TypeVar("ValueT", bound=(str | int))
""" `constraints: str, int` """
MetaT = TypeVar("MetaT") # , bound=object
# """ `constraints: object` """

class MetaEnum(Enum, Generic[ValueT, MetaT]):
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
# ============================================================================
# StrEnum
# ============================================================================
class BaseStrEnum(StrEnum):
    """
    `name = <string>`
    """
    
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
    def keys(cls): 
        """ 
        *`@returns`* `tuple(m.name for m in cls)` 
        """
        return cls.names()

    @classmethod
    def values(cls, unique: bool=True) -> tuple[str, ...]:
        """ 
        *`@returns`* 
        `tuple(m.value for m in cls) if not unique 
        else tuple(set(m.value for m in cls))` 
        """
        return (
            tuple(m.value for m in cls) if not unique
            else tuple(set(m.value for m in cls))
        )

    @classmethod
    def get(cls, key: str) -> Self:
        """ *`@returns`* `cls[key]` """
        return cls[key]

    @classmethod
    def contains(cls, key: str) -> bool:
        """ *`@returns`* `key in cls.__members__` """
        return key in cls.__members__

# ============================================================================
# IntEnum
# =============================================================================
class BaseIntEnum(IntEnum):
    """
    `name = <int>`
    """
    
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
    def keys(cls): 
        """ 
        *`@returns`* `tuple(m.name for m in cls)` 
        """
        return cls.names()

    @classmethod
    def values(cls) -> tuple[int, ...]:
        """ *`@returns`* `tuple(m.value for m in cls)` """
        return tuple(m.value for m in cls)

    @classmethod
    def get(cls, key: str) -> Self:
        """ *`@returns`* `cls[key]` """
        return cls[key]

    @classmethod
    def contains(cls, key: str) -> bool:
        """ *`@returns`* `key in cls.__members__` """
        return key in cls.__members__
