"""
*`@file`* `utils/safe`
"""
from typing import (Any, Literal, Callable, TypeVar, overload)
from inspect import getfullargspec
# thought I might have need for this during debugging, but mb unnecessary

VT = TypeVar('VT')


@overload
def readattr(
    obj: Any, 
    attr: str, 
    /, 
    use_repr: Literal[False]=False, 
    *, 
    missing_val: VT,
) -> VT: ...

@overload
def readattr(
    obj: Any, 
    attr: str, 
    /, 
    use_repr: bool=False, 
    *, 
    missing_val: Literal['<unavailable>'] | None='<unavailable>',
) -> Literal['<unavailable>'] | None: ...

def readattr(
    obj: Any, 
    attr: str, 
    /, 
    use_repr: bool=False, 
    *, 
    missing_val: Any | None=None
):
    try:
        _MISSING = object()
        value = getattr(obj, attr, _MISSING)
        return (
            missing_val if value is _MISSING 
            else value if (not use_repr) 
            else repr(value)
        )
    except Exception as e:
        return f"<unavailable> ({type(e).__name__}) {str(e)}"

def invoke_method(
    obj: Any, 
    method: str, 
    *args, 
    **kwargs
) -> (Any 
    | Literal["<unavailable>", "<not_callable>", "<method_failed>"] 
    | str
):
    """
    `getattr(obj, method)(*args, **kwargs)`
    """
    method_value = readattr(obj, method)
    if (isinstance(method_value, str)) and method_value == "<unavailable>":
        return "<unavailable>"
    if (not callable(method_value)):
        return "<not_callable>"
    try:
        return method_value(*args, **kwargs)
    except Exception as e:
        return f"<method_failed> method={getfullargspec(method_value)} ({type(e).__name__}) {str(e)}"

def execute_deferred(
    fn: Callable[[], Any],
    /,
) -> (Any 
    | Literal['<execution_failed>'] 
    | str
):
    try: 
        return fn()
    except Exception as e:
        return " ".join([
            "<execution_failed>",
            f"function={getfullargspec(fn) if callable(fn) else '<fn not_callable>'}",
            f"({type(e).__name__}) {str(e)}"
        ])


def to_str(value: Any, /, use_repr: bool=False) -> str | Literal["<unprintable>"]:
    try: 
        return (str(value) if (not use_repr) else repr(value))
    except Exception: 
        return "<unprintable>"


def attr_label(value: Any, attr: str, /) -> str:
    """
    *`@returns`* 
    `f"{value.__name__}.{attr}" 
    if isinstance(value, type) 
    else f"{type(value).__name__}.{attr}"`
    """
    try:
        if (isinstance(value, type)):
            return f"{value.__name__}.{attr}"
        return f"{type(value).__name__}.{attr}"
    except Exception:
        return f"<unknown>.{attr}"
