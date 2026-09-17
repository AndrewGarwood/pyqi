"""
*`@file`* `models/_sort`
"""
from dataclasses import dataclass
from typing import (Any, Generic, Self, TypeVar, TypedDict)
from .._json import (Serial)
from ._enum import (BaseStrEnum)
from enum import (auto, StrEnum, IntEnum)
from lute import LogMsg

class SortOrder(BaseStrEnum):
    ASCENDING = auto()
    DESCENDING = auto()
    
K = TypeVar("K", bound=(int | str | StrEnum | IntEnum | SortOrder))

class SortOptionsDict(TypedDict):
    on: str
    by: str
    order: Any
    """ `bound=(int | str | StrEnum | IntEnum | SortOrder)` """


@dataclass
class SortOptions(Serial[SortOptionsDict], Generic[K]):
    """
    `Generic[K], K = TypeVar("K", bound=(int | str | StrEnum | SortOrder))`
    ```
    on: str     # The dimension field to sort (e.g., "Product Line")
    by: str     # The aggregated data field name to sort by (e.g., "Sum of Stock Value")
    order: K
    ```
    """
    on: str
    by: str
    order: K

    @classmethod
    def from_dict(cls, data: SortOptionsDict | dict[str, Any]) -> Self:
        try:
            return cls(
                on=data['on'],
                by=data['by'],
                order=data['order']
            )
        except Exception as e:
            raise RuntimeError(LogMsg.err(
                e,
                received=str(data),
                expected=SortOptionsDict.__name__ 
            ))

    def to_dict(self) -> SortOptionsDict | dict[str, Any]:
        return {
            "on": self.on,
            "by": self.by,
            "order": self.order
        }