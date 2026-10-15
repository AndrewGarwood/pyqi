"""
*`@file`* `utils/safe`
"""
from typing import (Any, Literal)

# thought I might have need for this during debugging, but mb unnecessary


def readattr(obj: Any, attr: str, /, use_repr: bool=False) -> Any | Literal["<unavailable>"] | str:
    try:
        _MISSING = object()
        value = getattr(obj, attr, _MISSING)
        return (
            "<unavailable>" if value is _MISSING 
            else value if (not use_repr) 
            else repr(value)
        )
    except Exception as e:
        return f"<unavailable> ({type(e).__name__}) {str(e)}"

def invoke_method(obj: Any, method: str, *args, **kwargs) -> Any | Literal["<unavailable>", "<not_callable>", "<method_failed>"] | str:
    value = readattr(obj, method)
    if (isinstance(value, str)) and value == "<unavailable>":
        return "<unavailable>"
    if (not callable(value)):
        return "<not_callable>"
    try:
        return value(*args, **kwargs)
    except Exception as e:
        return f"<method_failed> ({type(e).__name__}) {str(e)}"

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
