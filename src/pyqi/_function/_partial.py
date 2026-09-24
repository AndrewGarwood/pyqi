"""
*`@file`* `_function/_partial`
"""

from __future__ import annotations
from collections.abc import Mapping
from typing import (
    Any, Generic, ParamSpec, 
    Callable, Concatenate, TypeVar, 
)

A = TypeVar("A")
B = TypeVar("B")
P = ParamSpec("P")
R = TypeVar("R")
""" Return Type """


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


class PartialSecond(Generic[A, B, P, R]):
    """
    Stores a callable and binds its first argument and all arguments following
    its second argument.

    The callable's second positional argument is supplied at invocation time.

    Type parameters:
        A:
            Type of the bound first argument.

        B:
            Type of the second argument supplied at invocation time.

        P:
            Parameter specification for the bound arguments following the
            second argument.

        R:
            Callable return type.
    """

    fn: Callable[Concatenate[A, B, P], R]
    _first: A
    _args: tuple[Any, ...]
    _kwargs: dict[str, Any]

    def __init__(
        self,
        fn: Callable[Concatenate[A, B, P], R],
        first: A,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        self.fn = fn
        self._first = first
        self._args = args
        self._kwargs = dict(kwargs)

    def __call__(self, arg: B, /) -> R:
        return self.invoke(arg)

    def invoke(self, arg: B, /) -> R:
        return self.fn(
            self._first,
            arg,
            *self._args,
            **self._kwargs,
        )

    @property
    def first(self) -> A:
        return self._first

    @property
    def args(self) -> tuple[Any, ...]:
        return self._args

    @property
    def kwargs(self) -> Mapping[str, Any]:
        return self._kwargs.copy()

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"fn={self.fn!r}, "
            f"first={self._first!r}, "
            f"args={self._args!r}, "
            f"kwargs={self._kwargs!r})"
        )