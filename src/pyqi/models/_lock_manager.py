"""
*`@file`* `models/_lock_manager`
"""
import threading
from contextlib import contextmanager
import time
from lute import get_logger, LogMsg

class LockManager:
    """ 
    in `__init__`:
    - `self._lock = threading.RLock()`
    - `self._claimed = set() # set[int]`
    """
    _claimed: set[int]
    def __init__(self, name: str="LockManager"):
        self.name=name
        self._claimed = set()
        self._lock = threading.RLock()
        self.log = get_logger(name)

    def acquire(self, blocking: bool=True, timeout: float=-1):
        acquired = self._lock.acquire(blocking=blocking, timeout=timeout)
        return acquired
    
    def release(self):
        self._lock.release()

    def claim_handle(self, handle: int, /):
        with self._lock:
            if handle in self._claimed: 
                return False
            self._claimed.add(handle)
            return True

    def release_handle(self, handle: int, /):
        with self._lock:
            self._claimed.discard(handle)

    @contextmanager
    def engage_lock(self, sleep: float=0.25):
        thread = f"{threading.current_thread().name}"
        start = time.monotonic()
        self.acquire(blocking=True)
        acquired = time.monotonic()
        self.log.debug(LogMsg(
            f"{self.name} acquired lock",
            thread=thread,
            wait_time=f"{acquired - start:.2f}s"
        ))
        try:
            time.sleep(sleep)
            yield
        finally:
            self.log.debug(LogMsg(
                f"{self.name} releasing lock",
                thread=thread,
                held_time=f"{time.monotonic() - acquired:.2f}s"
            ))
            self.release()


__all__ = [
    "LockManager"
]