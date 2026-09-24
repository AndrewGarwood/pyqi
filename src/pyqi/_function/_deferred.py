"""
*`@file`* `_function/_deferred`
"""
from __future__ import annotations
from typing import (
    Generic, ParamSpec, 
    Callable, TypeVar, 
)

P = ParamSpec("P")
R = TypeVar("R")
""" Return Type """

class Deferred(Generic[P, R]):
    fn: Callable[P, R]
    def __init__(
            self, 
            fn: Callable[P, R], 
            /,
            *args: P.args, 
            **kwargs: P.kwargs
        ):
        self.fn = fn
        self._args=args
        self._kwargs=kwargs

    def __call__(self):
        return self.invoke()
    
    def invoke(self) -> R:
        return self.fn(*self._args, **self._kwargs)
    
    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"fn={self.fn!r}, "
            f"args={self._args!r}, "
            f"kwargs={self._kwargs!r})"
        )
