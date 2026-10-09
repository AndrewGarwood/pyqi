"""
*`@file`* `pyqi/models/_registry`
"""
from __future__ import annotations
from collections.abc import (Callable, Mapping)
from typing import (Any, Generic, TypeVar, cast)
from ._enum import BaseStrEnum
from enum import StrEnum
from ..utils import export

import lute
LogMsg = lute.LogMsg

K = TypeVar("K", bound=StrEnum)
R = TypeVar("R")
F = TypeVar("F", bound=Callable[..., Any])

class Registry(Generic[K, R]):
    """
    *`@extends`* `Generic[K, R]`
        - `K` registry key type
        - `R` return type of registry values (values are `Callable[..., R]`)
    Registry mapping normalized keys to callables with a common return type.
    """
    _normalize_key: Callable[[K | str], K]
    def __init__(
        self,
        enum_type: type[K],
        normalize_key: Callable[[K | str], K] | None = None,
        name: str | None=None,
    ) -> None:
        """
        - enum_type (type[K]): enum class
        - name (str, optional): _description_. Defaults to "registry".
        - normalize_key (Callable[[K | str], K]): 
            - can pass in enum_type.resolve() if enum_type extends BaseStrEnum
        """
        self._name = name or f"Registry<{enum_type.__name__}>"
        self._enum = enum_type
        normalizer = (
            normalize_key if normalize_key is not None 
            else enum_type.resolve if issubclass(enum_type, BaseStrEnum) 
            else None
        )
        if (not normalizer):
            raise RuntimeError(LogMsg(
                f"argument 'normalize_key' is required when enum_type is not BaseStrEnum"
            ))
        self._normalize_key = normalizer
        self._functions: dict[K, Callable[..., R]] = dict()
        

    @property
    def name(self) -> str: 
        return self._name

    def normalize_key(self, key: K | str) -> K: 
        return self._normalize_key(key)
    
    def register(
        self,
        key: K | str,
        *,
        replace: bool = False,
    ) -> Callable[[F], F]:
        """
        Return a decorator that registers a callable under `key`.

        The decorator preserves the concrete callable type, including its
        original argument signature.
        """
        normalized_key = self.normalize_key(key)

        def decorator(function: F) -> F:
            if not callable(function):
                raise TypeError(LogMsg(
                    f"Registered value must be callable, got "
                    f"{type(function).__name__}"
                ))
            if not replace and normalized_key in self._functions:
                existing = self._functions[normalized_key]
                raise DuplicateRegistrationError(LogMsg(
                    f"{normalized_key!r} is already registered in {self._name!r}",
                    existing=self._callable_name(existing),
                    proposed=self._callable_name(function)
                ))
            # The registry guarantees the common return type through its
            # public contract. Python cannot statically enforce that F
            # returns exactly R while also preserving F's full signature.
            self._functions[normalized_key] = cast(
                Callable[..., R],
                function,
            )
            return function
        return decorator

    def add(
        self,
        key: K | str,
        function: Callable[..., R],
        *,
        replace: bool = False,
    ) -> None:
        """Register a function without decorator syntax."""
        self.register(key, replace=replace)(function)

    def get(self, key: K | str) -> Callable[..., R]:
        """Return the callable registered under `key`."""
        normalized_key = self.normalize_key(key)

        try:
            return self._functions[normalized_key]
        except KeyError as e:
            raise RegistryKeyError(
                f"{normalized_key!r} is not registered in {self._name!r}"
            ) from e

    def call(
        self,
        key: K | str,
        /,
        *args,
        **kwargs,
    ) -> R:
        """Call the function registered under `key`."""
        normalized_key = self.normalize_key(key)
        function = self.get(normalized_key)
        try:
            return function(*args, **kwargs)
        except Exception as e:
            raise RegistryCallError(
                f"Error calling {normalized_key!r} from {self._name!r}; "
                f"function={self._callable_name(function)!r}, "
                f"args={args!r}, kwargs={kwargs!r}"
            ) from e

    def unregister(self, key: K | str, /) -> Callable[..., R]:
        """Remove and return the callable registered under `key`."""
        return self.pop(key)

    def is_registered(self, key: K | str, /) -> bool:
        return self.__contains__(key)

    def keys(self):
        return self._functions.keys()
    def values(self):
        return self._functions.values()
    def items(self):
        return self._functions.items()
    
    def as_mapping(self) -> Mapping[K, Callable[..., R]]:
        """
        Return a read-only view of the registry.
        - Mutations to the registry remain visible through the returned view.
        """
        from types import MappingProxyType
        return MappingProxyType(self._functions)

    def pop(self, key: K | str, /) -> Callable[..., R]:
        """Remove and return the callable registered under `key`."""
        normalized_key = self.normalize_key(key)
        try:
            return self._functions.pop(normalized_key)
        except KeyError as e:
            raise RegistryKeyError(
                f"{normalized_key!r} is not registered in {self._name!r}"
            ) from e
    
    def __len__(self) -> int: 
        return len(self._functions)
    
    def __iter__(self): 
        return iter(self._functions)
    
    def __contains__(self, key: object, /) -> bool:
        try:
            normalized_key = self.normalize_key(cast(K | str, key))
        except RegistryKeyError:
            return False
        return normalized_key in self._functions

    @staticmethod
    def _callable_name(function: Callable[..., Any]) -> str:
        return getattr(
            function,
            "__qualname__",
            getattr(function, "__name__", type(function).__name__),
        )



class RegistryError(Exception):
    """Base registry-related exception."""

class DuplicateRegistrationError(RegistryError):
    """Raised when attempting to register an existing key."""

class RegistryKeyError(RegistryError, KeyError):
    """Raised when a registry key cannot be resolved or is not registered."""

class RegistryCallError(RegistryError):
    """Raised when a registered callable fails."""

__all__ = export(
    Registry, 
)