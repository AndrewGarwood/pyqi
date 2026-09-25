"""
*`@file`* `fs/_path.py`
"""
import os, re
from datetime import date, datetime
from pathlib import Path, PurePath
from typing import Callable, Literal, Optional
from lute import LogMsg
from .types import (StrPath, TargetExt, DataExt)
from .._dt._format import FormatString
from .. import _string as String


def normalize_ext_input(ext: TargetExt) -> list[str | DataExt]:
    return (
        [ext] if isinstance(ext, str) and bool(ext)
        else list(ext) if ext is not None 
        else []
    )

def has_target_ext(
    s: StrPath,
    target_ext: TargetExt
) -> bool:
    targets = normalize_ext_input(target_ext) 
    return bool(targets) and any(
        to_path(s).suffix.casefold() == ext.casefold() 
        for ext in targets
    ) 

def normalized(path: StrPath, /):
    """ *`@returns`* `os.path.normcase(os.path.abspath(os.fspath(str(path))))` """
    return os.path.normcase(os.path.abspath(os.fspath(str(path))))


def to_path(
    p: StrPath | PurePath, 
    /, 
    expanduser: bool | Literal['auto']=False, 
    resolve: bool=True
) -> Path:
    """ 
    *`@returns`* `(Path(p) if not isinstance(p, Path) else p)`
    - `if resolve: return p.resolve()`
    - `if expanduser == 'auto'` `return p.expanduser() if p starts with '~'`
    """
    p = Path(p) if not isinstance(p, Path) else p
    should_expand = (
        (expanduser=='auto' and str(p).startswith('~')) or expanduser
    )
    if (should_expand): p = p.expanduser()
    if (resolve): p = p.resolve()
    return p

def is_file(p: StrPath, /) -> bool:
    """ *`@returns`* `str(p) != "." and p.is_file()` """
    p = to_path(p or '')
    return (str(p) != "." and p.is_file())

def is_dir(p: StrPath, /) -> bool:
    """ *`@returns`* `str(p) != "." and p.is_dir()` """
    p = to_path(p or '')
    return (str(p) != "." and p.is_dir())


def lname(
    p: StrPath, 
    /, 
    prefix: Optional[Literal['~', '$', '...'] | str]='~'
):
    p = to_path(p)
    prefix = '' if prefix is None else prefix
    return f"{prefix}{p.parent.name}/{p.name}"


def sanitize_filename(value: str) -> str:
    value = value.strip()
    value = re.sub(r'[\\/:*?"<>|]+', "_", value)
    value = re.sub(r"(?<!^)_+", "_", value)
    return value


def dated_folder(base: StrPath="", ref: date | None = None, suffix: str="", fmt: str=FormatString.YMD_DOT) -> Path:
    """ *`@returns`* path to `'{base}/{datestamp(ref)}'` 
        - `'{base}/{datestamp(ref)}_{suffix}'` `if suffix is not None `
        - `'{datestamp(ref)}_{suffix}'` `if base is None`
    """
    if ref is None: ref = date.today()
    folder_name = ref.strftime(fmt)
    if suffix:
        folder_name += f"_{suffix}"
    return Path(base).joinpath(folder_name) if base else Path(folder_name)

def dated_filename(
    base: str="",
    ext: Optional[DataExt | str] = None,
    ref: date | datetime | None = None,
    fmt: FormatString | str=FormatString.YMD_DOT,
) -> str:
    """ 
    *`@returns`* `f"{datestamp(ref)}_{sanitize_filename(base)}{extension}"`
    - `f"{datestamp(ref)}{ext}"` if base is empty string
    - prepends `'.'` to extension if not present
    """
    ext = (
        Path(base).suffix if not ext
        else f".{ext}" if ext and not ext.startswith('.') 
        else ext
    )

    if (not ext):
        raise ValueError(LogMsg(
            f"Unable to resolve file extension (path.suffix) from arguments",
            base=base,
            ext=ext
        ))

    sanitized = sanitize_filename(base)
    filename = (
        f"{sanitized}{ext}" 
        if not sanitized.lower().endswith(ext.lower()) 
        else sanitized
    )
    if ref is None: ref = date.today()
    _datestamp = ref.strftime(fmt)
    return f"{_datestamp}_{filename}" if filename != ext else f"{_datestamp}{ext}"



def is_nonlocal(
    p: StrPath,
    /,
    *condition: Callable[[str], bool]
) -> bool:
    """ 
    - `i.e. should_stage_file`
    
    *`@param`* `condition`
        - e.g. `condition = Function.Partial(String.contains, 'onedrive - ', ignore_case=True)`
    *`@returns`* 
        - `String.startswith(str(p).casefold(), ("http://", "https://"))` or `any` conditions satisfied
        - `len(condition)=0` -> only check `if startswith(...)`
    """
    return (
        String.startswith(str(p).casefold(), ("http://", "https://"))
        or (
            any(c(str(p)) for c in condition) if condition 
            else False
        )
    )