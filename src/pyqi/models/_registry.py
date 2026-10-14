"""
*`@file`* `pyqi/models/_registry`
"""
from __future__ import annotations
from collections.abc import (Callable, Mapping)
from typing import (Any, Generic, TypeVar, cast, ParamSpec)
from ._enum import BaseStrEnum
from enum import StrEnum
from ..utils import export

import lute
LogMsg = lute.LogMsg

K = TypeVar("K", bound=StrEnum)
P = ParamSpec("P")
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
        self._enum_type = enum_type
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

    @property
    def enum_type(self) -> type[K]:
        return self._enum_type

    def normalize_key(self, key: K | str) -> K: 
        try:
            return self._normalize_key(key)
        except RegistryKeyError:
            raise
        except (KeyError, TypeError, ValueError) as e:
            raise RegistryKeyError(
                f"Invalid key for {self._name}: {key!r}"
            ) from e
    
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
                    existing=lute.annotate(existing),
                    proposed=lute.annotate(function)
                ))
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
            raise RegistryCallError(LogMsg(
                f"Error calling {normalized_key!r} from {self._name!r};",
                registered_function=lute.annotate(function),
                args=str(args),
                kwargs=str(kwargs)
            )) from e

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


class TypedRegistry(Generic[K, P, R]):
    """
    Registry for functions that all have the same parameter signature
    and return type.

    Type parameters:
        `K`: Canonical registry key type.

        `P`: Parameter specification shared by every registered function.

        `R`: Return type shared by every registered function.
    """

    def __init__(
        self,
        enum_type: type[K],
        *,
        normalize_key: Callable[[K | str], K],
        name: str | None = None,
    ) -> None:
        self._enum_type = enum_type
        self._normalize_key = normalize_key
        self._name = name or f"{type(self).__name__}<{enum_type.__name__}>"
        self._functions: dict[K, Callable[P, R]] = {}

    @property
    def name(self) -> str: 
        return self._name

    @property
    def enum_type(self) -> type[K]:
        return self._enum_type

    def normalize_key(self, key: K | str) -> K: 
        try:
            return self._normalize_key(key)
        except RegistryKeyError:
            raise
        except (KeyError, TypeError, ValueError) as e:
            raise RegistryKeyError(
                f"Invalid key for {self._name}: {key!r}"
            ) from e

    def register(
        self,
        key: K | str,
        /,
        *,
        replace: bool = False,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """
        Return a decorator that registers a function.

        The registered function must match the registry's complete call
        signature, including positional parameters, keyword parameters,
        and return type.
        """
        normalized_key = self.normalize_key(key)

        def decorator(
            function: Callable[P, R],
        ) -> Callable[P, R]:
            if not replace and normalized_key in self._functions:
                existing = self._functions[normalized_key]

                raise DuplicateRegistrationError(LogMsg(
                    f"{normalized_key!r} is already registered.",
                    registry_name=self._name,
                    existing=lute.annotate(existing),
                    proposed=lute.annotate(function)
                ))
            self._functions[normalized_key] = function
            return function
        return decorator

    def unregister(
        self,
        key: K | str,
        /,
    ) -> Callable[P, R]:
        return self.pop(key)

    def add(
        self,
        key: K | str,
        function: Callable[P, R],
        /,
        *,
        replace: bool = False,
    ) -> Callable[P, R]:
        """
        Register a function without decorator syntax.

        Returns the registered function for symmetry with `register`.
        """
        return self.register(
            key,
            replace=replace,
        )(function)

    def get(
        self,
        key: K | str,
        /,
    ) -> Callable[P, R]:
        """Return the function registered under `key`."""
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
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """
        Call the function registered under `key`.

        Both args and kwargs are statically checked against `P`.
        """
        normalized_key = self.normalize_key(key)
        function = self.get(normalized_key)

        try:
            return function(*args, **kwargs)
        except Exception as e:
            raise RegistryCallError(LogMsg(
                f"Error calling {normalized_key!r} from {self._name!r};",
                registered_function=lute.annotate(function),
                args=str(args),
                kwargs=str(kwargs)
            )) from e

    def pop(self, key: K | str, /) -> Callable[P, R]:
        """Remove and return the callable registered under `key`."""
        normalized_key = self.normalize_key(key)
        try:
            return self._functions.pop(normalized_key)
        except KeyError as e:
            raise RegistryKeyError(
                f"{normalized_key!r} is not registered in {self._name!r}"
            ) from e
    

    def as_mapping(self) -> Mapping[K, Callable[P, R]]:
        """
        Return a read-only view of the registry.
        - Mutations to the registry remain visible through the returned view.
        """
        from types import MappingProxyType
        return MappingProxyType(self._functions)
    
    def keys(self):
        return self._functions.keys()

    def values(self):
        return self._functions.values()

    def items(self):
        return self._functions.items()

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

class RegistryError(Exception):
    """Base registry-related exception."""

class DuplicateRegistrationError(RegistryError):
    """Raised when attempting to register an existing key."""

class RegistryKeyError(RegistryError, KeyError):
    """Raised when a registry key cannot be resolved or is not registered."""

class RegistryCallError(RegistryError):
    """Raised when a registered callable fails."""

__all__ = export(
    Registry, TypedRegistry
)