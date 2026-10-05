"""
*`@file`* `models/_lock_manager`
"""
import threading

class LockManager:
    _claimed: set[int]
    def __init__(self, name: str="LockManager"):
        self.name=name
        self._claimed = set()
        self._lock = threading.RLock()

    def try_claim(self, handle: int, /):
        with self._lock:
            if handle in self._claimed: 
                return False
            self._claimed.add(handle)
            return True

    def release(self, handle: int, /):
        with self._lock:
            self._claimed.discard(handle)

__all__ = [
    "LockManager"
]