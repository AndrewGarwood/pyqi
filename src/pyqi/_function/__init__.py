"""
*`@module`* `_function/__init__.py`
"""
from __future__ import annotations
from typing import (
    Generic, ParamSpec, 
    Callable, Concatenate, TypeVar, 
)

A = TypeVar("A")
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

class Partial(Generic[A, P, R]):
    """
    `Generic[A, P, R]`
    - Stores a callable and bound arguments for later execution.

    - `A` is ParamSpec for value(s) supplied at runtime and positioned before `P` in signature of `fn`
    """
    fn: Callable[Concatenate[A, P], R]

    def __init__(
            self, 
            fn: Callable[Concatenate[A, P], R], 
            /,
            *args: P.args, 
            **kwargs: P.kwargs
        ):
        self.fn = fn
        self._args=args
        self._kwargs=kwargs
    def __call__(self, arg: A, /):
        return self.invoke(arg)
    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs
    
    def invoke(self, arg: A, /) -> R:
        return self.fn(arg, *self._args, **self._kwargs)
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"fn={self.fn!r}, "
            f"args={self._args!r}, "
            f"kwargs={self._kwargs!r})"
        )
    
    def __name__(self) -> str:
        return "PartialFunction"

