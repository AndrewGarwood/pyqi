"""
*`@file`* `models/_flow`
"""
from dataclasses import dataclass
from typing import (Generic, TypeVar)
from enum import StrEnum
from datetime import datetime


StageT = TypeVar("StageT", bound=(StrEnum))

@dataclass(frozen=True, slots=True)
class StageTransition(Generic[StageT]):
    previous: StageT
    current: StageT
    changed_at: datetime


class Flow(Generic[StageT]):
    ...