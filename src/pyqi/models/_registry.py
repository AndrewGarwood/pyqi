"""
*`@file`* `pyqi/models/_registry`
"""
from __future__ import annotations
from collections.abc import (Callable, Mapping)
from types import MappingProxyType
from typing import (Any, Generic, Iterator, TypeVar, cast, ParamSpec)
from ._enum import BaseStrEnum
from enum import StrEnum
from ..utils import export

import lute
LogMsg = lute.LogMsg

# TODO: separate files...

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
            raise RegistryCallError(LogMsg.err(e,
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
            raise RegistryKeyError(LogMsg.err(e,
                f"{normalized_key!r} is not registered in {self._name!r}"
            )) from e
    def __getitem__(
        self,
        key: K | str,
        /,
    ) -> Callable[..., R]:
        """Return the callable registered under ``key``."""
        return self.get(key)
    
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

    `Type parameters:`
        `K = TypeVar("K", bound=StrEnum)` Canonical registry key type.

        `P = ParamSpec("P")` Parameter specification shared by every registered function.

        `R = TypeVar("R")` Return type shared by every registered function.

    example:
    ```
    EXPORT_METHOD_REGISTRY: TypedRegistry[
        ExportMethod, 
        [
            Session, 
            ExportOptions, 
            NativeSaveDialogOptions 
                | Callable[..., NativeSaveDialogOptions] 
                | None
        ], 
        Result[ExportDetails]
    ] = TypedRegistry(
        ExportMethod, 
        normalize_key=ExportMethod.resolve, 
        name="ExportMethodRegistry"
    )
    ```
    example:
    ```
    STRING_CONDITION_REGISTRY: TypedRegistry[
        StringCondition,
        [
            str,
            StrInput | Any,
            bool,
            bool,
        ],
        bool
    ] = TypedRegistry(
        StringCondition, 
        normalize_key=StringCondition.resolve, 
        name="StringConditionRegistry"
    )
    ```
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
            raise RegistryKeyError(LogMsg.err(
                e,
                f"Invalid key for {self._name}: {key!r}"
            )) from e

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
    
    def __getitem__(
        self,
        key: K | str,
        /,
    ) -> Callable[P, R]:
        """Return the callable registered under ``key``."""
        return self.get(key)
    
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


class CallableRegistry(Generic[K, F]):
    """
    Registry whose values conform to a common callable type.

    Unlike ``TypedRegistry``, the callable contract is represented directly
    by ``F`` rather than by a ``ParamSpec`` and return type.

    This is particularly useful when ``F`` is a callable ``Protocol`` that
    expresses:

    - Parameter names
    - Positional-only parameters
    - Keyword-only parameters
    - Default values
    - Overloads
    - The return type

    Type parameters:
        `K`
            Canonical registry key type. Must extend ``StrEnum``.

        `F`
            Callable type shared by every registered value. This will
            commonly be a callable ``Protocol``.

    Important:
        Python's type system cannot extract a ``ParamSpec`` or return type
        from an arbitrary callable type variable ``F``. Consequently,
        ``get()`` preserves the complete callable type, but ``call()`` must
        accept dynamically typed arguments and return ``Any``.

        Prefer this:
        ```
        registry.get(key)(
            value,
            expected,
            ignore_case=True,
            require_all=False,
        )
        ```
        when full call-site type checking is important.

    Example:
    ```
    class StringPredicate(Protocol):
        def __call__(
            self,
            value: str,
            other: StrInput | Any,
            *,
            ignore_case: bool = False,
            require_all: bool = False,
        ) -> bool: ...

    STRING_CONDITION_REGISTRY: CallableRegistry[
        StringCondition,
        StringPredicate,
    ] = CallableRegistry(
        StringCondition,
        normalize_key=StringCondition.resolve,
        name="StringConditionRegistry",
    )
    ```
    """

    _enum_type: type[K]
    _normalize_key: Callable[[K | str], K]
    _name: str
    _functions: dict[K, F]

    def __init__(
        self,
        enum_type: type[K],
        *,
        normalize_key: Callable[[K | str], K] | None = None,
        name: str | None = None,
    ) -> None:
        """
        Initialize the registry.

        Args:
            enum_type:
                Enum class used for registry keys.

            normalize_key:
                Function that converts a key or string into the canonical
                enum member.

                When omitted and ``enum_type`` extends ``BaseStrEnum``,
                ``enum_type.resolve`` is used.

            name:
                Human-readable registry name used in diagnostics.

        Raises:
            RuntimeError:
                If ``normalize_key`` is omitted and ``enum_type`` does not
                extend ``BaseStrEnum``.
        """
        self._enum_type = enum_type
        self._name = (
            name
            or f"{type(self).__name__}<{enum_type.__name__}>"
        )

        normalizer = (
            normalize_key
            if normalize_key is not None
            else enum_type.resolve
            if issubclass(enum_type, BaseStrEnum)
            else None
        )

        if normalizer is None:
            raise RuntimeError(
                LogMsg(
                    "argument 'normalize_key' is required when "
                    "enum_type is not BaseStrEnum",
                    registry_name=self._name,
                    enum_type=enum_type.__name__,
                )
            )

        self._normalize_key = normalizer
        self._functions = {}

    @property
    def name(self) -> str:
        """Return the human-readable registry name."""
        return self._name

    @property
    def enum_type(self) -> type[K]:
        """Return the enum type used for registry keys."""
        return self._enum_type

    def normalize_key(
        self,
        key: K | str,
        /,
    ) -> K:
        """
        Resolve a key to its canonical enum member.

        Raises:
            RegistryKeyError:
                If the key cannot be resolved.
        """
        try:
            return self._normalize_key(key)
        except RegistryKeyError:
            raise
        except (KeyError, TypeError, ValueError) as e:
            raise RegistryKeyError(
                LogMsg.err(
                    e,
                    f"Invalid key for {self._name}: {key!r}",
                )
            ) from e

    def register(
        self,
        key: K | str,
        /,
        *,
        replace: bool = False,
    ) -> Callable[[F], F]:
        """
        Return a decorator that registers a callable under ``key``.

        The callable must be statically compatible with ``F``.

        The decorator returns the original callable unchanged.

        Args:
            key:
                Registry key or string representation of one.

            replace:
                Whether an existing registration may be replaced.

        Raises:
            TypeError:
                If the supplied value is not callable at runtime.

            DuplicateRegistrationError:
                If ``key`` is already registered and ``replace`` is false.
        """
        normalized_key = self.normalize_key(key)

        def decorator(function: F) -> F:
            if not callable(function):
                raise TypeError(
                    LogMsg(
                        "Registered value must be callable.",
                        registry_name=self._name,
                        key=repr(normalized_key),
                        received_type=type(function).__name__,
                    )
                )

            if (
                not replace
                and normalized_key in self._functions
            ):
                existing = self._functions[normalized_key]

                raise DuplicateRegistrationError(
                    LogMsg(
                        f"{normalized_key!r} is already registered.",
                        registry_name=self._name,
                        existing=lute.annotate(existing),
                        proposed=lute.annotate(function),
                    )
                )

            self._functions[normalized_key] = function
            return function

        return decorator

    def add(
        self,
        key: K | str,
        function: F,
        /,
        *,
        replace: bool = False,
    ) -> F:
        """
        Register a callable without decorator syntax.

        Returns:
            The original registered callable.
        """
        return self.register(
            key,
            replace=replace,
        )(function)

    def get(
        self,
        key: K | str,
        /,
    ) -> F:
        """
        Return the callable registered under ``key``.

        The returned value retains the callable type represented by ``F``.

        Raises:
            RegistryKeyError:
                If the key is valid but is not registered.
        """
        normalized_key = self.normalize_key(key)

        try:
            return self._functions[normalized_key]
        except KeyError as e:
            raise RegistryKeyError(
                LogMsg.err(
                    e,
                    f"{normalized_key!r} is not registered "
                    f"in {self._name!r}",
                )
            ) from e

    def call(
        self,
        key: K | str,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Call the callable registered under ``key``.

        Warning:
            Arguments and the return value cannot be statically derived from
            ``F``. Use ``get(key)(...)`` when full call-site type checking is
            required/preferred.

        Raises:
            RegistryCallError:
                If the registered callable raises an exception.
        """
        normalized_key = self.normalize_key(key)
        function = self.get(normalized_key)

        try:
            return function(*args, **kwargs)
        except Exception as e:
            raise RegistryCallError(
                LogMsg.err(
                    e,
                    f"Error calling {normalized_key!r} "
                    f"from {self._name!r};",
                    registered_function=lute.annotate(function),
                    args=repr(args),
                    kwargs=repr(kwargs),
                )
            ) from e

    def unregister(
        self,
        key: K | str,
        /,
    ) -> F:
        """
        Remove and return the callable registered under ``key``.

        Raises:
            RegistryKeyError:
                If the key is valid but is not registered.
        """
        return self.pop(key)

    def pop(
        self,
        key: K | str,
        /,
    ) -> F:
        """
        Remove and return the callable registered under ``key``.

        Raises:
            RegistryKeyError:
                If the key is valid but is not registered.
        """
        normalized_key = self.normalize_key(key)

        try:
            return self._functions.pop(normalized_key)
        except KeyError as e:
            raise RegistryKeyError(
                LogMsg.err(
                    e,
                    f"{normalized_key!r} is not registered "
                    f"in {self._name!r}",
                )
            ) from e

    def is_registered(
        self,
        key: K | str,
        /,
    ) -> bool:
        """Return whether ``key`` has a registered callable."""
        return key in self

    def keys(self):
        """Return a dynamic view of registered keys."""
        return self._functions.keys()

    def values(self):
        """Return a dynamic view of registered callables."""
        return self._functions.values()

    def items(self):
        """Return a dynamic view of registry entries."""
        return self._functions.items()

    def as_mapping(self) -> Mapping[K, F]:
        """
        Return a read-only, dynamic view of the registry.

        Subsequent registry mutations remain visible through the returned
        mapping.
        """
        return MappingProxyType(self._functions)

    def __getitem__(
        self,
        key: K | str,
        /,
    ) -> F:
        """Return the callable registered under ``key``."""
        return self.get(key)

    def __len__(self) -> int:
        """Return the number of registered callables."""
        return len(self._functions)

    def __iter__(self) -> Iterator[K]:
        """Iterate over registered keys."""
        return iter(self._functions)

    def __contains__(
        self,
        key: object,
        /,
    ) -> bool:
        """Return whether ``key`` resolves to a registered key."""
        try:
            normalized_key = self.normalize_key(
                cast(K | str, key)
            )
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
    Registry, TypedRegistry, CallableRegistry
)