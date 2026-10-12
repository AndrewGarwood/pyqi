"""
*`@file`* `models/_telemetry`
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import time
from ..utils import export

@dataclass(slots=True)
class Telemetry:
    """ 
    - *`@method`* `start()` sets `_started_at` and `_started_monotonic` 
    - *`@method`* `stop()` sets `_ended_at` and `_ended_monotonic`
    """
    _started_at: Optional[datetime] = None
    _ended_at: Optional[datetime] = None
    _started_monotonic: Optional[float] = None
    _ended_monotonic: Optional[float] = None

    def start(self) -> None:
        if self._started_monotonic is not None:
            raise RuntimeError("Telemetry has already been started")
        self._started_at = datetime.now()
        self._ended_at = None
        self._started_monotonic = time.monotonic()
        self._ended_monotonic = None

    def stop(self) -> None:
        if self._started_monotonic is None:
            raise RuntimeError("Telemetry has not been started")
        if self._ended_monotonic is not None:
            return
        self._ended_at = datetime.now()
        self._ended_monotonic = time.monotonic()

    def reset(self) -> None:
        self._started_at = None
        self._ended_at = None
        self._started_monotonic = None
        self._ended_monotonic = None

    @property
    def running(self) -> bool:
        return (
            self._started_monotonic is not None
            and self._ended_monotonic is None
        )

    @property
    def elapsed(self) -> Optional[float]:
        """ 
        *`@returns`* `(self._ended_monotonic or time.monotonic()) - (self._started_monotonic)`
        - or `None` `if self._started_monotonic is None`
        """
        if self._started_monotonic is None:
            return None
        end = self._ended_monotonic or time.monotonic()
        return end - self._started_monotonic


__all__ = export(Telemetry)