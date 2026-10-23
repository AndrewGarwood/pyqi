"""
*`@file`* `fs/_search.py`
"""
import os
from pathlib import Path
from typing import (Optional, Callable)
from lute import LogMsg
from .types import (StrPath, TargetExt)
from ._path import (to_path, has_target_ext, normalize_ext_input, lname)
from .. import (_array as Array, _dt as dt)

def get_directory_files(
    dir: StrPath, 
    target_ext: Optional[TargetExt]=None, 
    recursive: bool=False, 
    filter_fn: Optional[Callable[[str], bool]]=None
) -> list[Path]: # , exclude_dirs: list[str]=['.archive']
    target_files: list[Path] = []
    dir = to_path(dir)
    walk = list(os.walk(dir))
    walk_limit = min(1, len(walk)) if not recursive else len(walk)
    for i in range(walk_limit):
        (root, _, files) = walk[i]
        if (not len(files)): continue
        _to_add: list[Path] = []
        for f in files:
            invalid_ext = bool(target_ext) and not has_target_ext(f, target_ext)
            if invalid_ext: continue
            _path = Path(root).joinpath(f)
            should_add = (
                not filter_fn 
                or (filter_fn(_path.stem) or filter_fn(_path.name))
                )
            if (should_add): _to_add.append(_path)
        target_files.extend(_to_add)
    return target_files

def find_file(
    parent: StrPath, 
    /,
    target_ext: Optional[TargetExt]=None, 
    recursive: bool=False, 
    filter_fn: Optional[Callable[[str], bool]]=None,
    require_unique: bool=True
) -> Path:
    try:
        candidates = get_directory_files(parent, target_ext, recursive, filter_fn)
        if not candidates:
            raise FileNotFoundError(f"Found 0 files that match parameters")
        if require_unique and len(candidates) > 1:
            raise RuntimeError(
                f"Found multiple ({len(candidates)}) files & {require_unique=}"
            )
        return candidates[0]
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            error=e,
            parent=str(parent),
            target_ext=str(target_ext),
            recursive=recursive,
        ))


def find_dir(
    parent: StrPath,  
    recursive: bool=False,
    filter_fn: Optional[Callable[[str], bool]]=None,
) -> list[Path]:
    parent = to_path(parent)
    walk = list(os.walk(parent))
    walk_limit = min(1, len(walk)) if not recursive else len(walk)
    target_dirs: list[Path] = []
    for i in range(walk_limit):
        (root, dirs, _) = walk[i]
        filtered = Array.filter(dirs, filter_fn) if filter_fn else dirs
        target_dirs.extend([Path(root).joinpath(d) for d in filtered])
    return target_dirs


def remove_from_dir(
    dir: StrPath,
    /,
    target_ext: Optional[TargetExt]=None,
    recursive: bool=False, 
    filter_fn: Optional[Callable[[str], bool]]=None
) -> list[Path]:
    removed: list[Path] = []
    try:
        target_files = get_directory_files(
            dir, 
            target_ext, 
            recursive, 
            filter_fn
        )
        for f in target_files:
            f.unlink()
            removed.append(f)
        return removed
    except Exception as e:
        raise Exception(LogMsg.err(
            error=e,
            dir=dir,
            target_ext=target_ext,
        )) from e



def get_most_recent_dir(
    parent: StrPath,
    /,
    fmt: str,
    get_date_str: Callable[[str], str]=lambda x: x[:10],
    recursive: bool=False,
    filter_fn: Optional[Callable[[str], bool]]=None,
) -> Path:
    parent = to_path(parent)
    target_dirs: list[str] = []
    walk = list(os.walk(parent))
    walk_limit = min(1, len(walk)) if not recursive else len(walk)
    for i in range(walk_limit):
        (root, dirs, _) = walk[i]
        before_filter_len = len(target_dirs)
        if filter_fn:
            target_dirs = Array.filter(dirs, filter_fn)
        else: # default filter
            target_dirs = Array.filter(dirs, lambda x: dt.matches_format(get_date_str(x), fmt))
        if not target_dirs:
            raise RuntimeError(LogMsg(
                f"No directories found under {parent=}",
                before_filter_len=before_filter_len,
                walk_root=root,
                available_dirs=str(dirs)
            ))
        target_dirs.sort(
            key=get_date_str,
            reverse=True
        )
    if not target_dirs:
        raise FileNotFoundError(LogMsg(
            f"No valid dir found in {lname(parent)}.",
            f"{os.listdir(parent)=}"
        ))
    return parent.joinpath(target_dirs[0])

def get_timesorted_files(
    parent: StrPath,
    /,
    fmt: str,
    get_date_str: Optional[Callable[[str], str]]=None,
    target_ext: TargetExt | None=None,
    descending: bool=True,
    filter_fn: Optional[Callable[[str], bool]]=None
) -> list[Path]:
    target_files = get_directory_files(
        parent, 
        target_ext, 
        False, 
        filter_fn
    )
    target_ext = normalize_ext_input(target_ext) if target_ext else []
    if not target_files:
        raise RuntimeError(LogMsg(
            f"No target files found under {parent=}",
            used_filter=bool(filter_fn),
            target_ext=str(target_ext)
        ))
    get_date_str = (
        (lambda s: s.split("_", 1)[0]) if get_date_str is None 
        else get_date_str
    )
    target_files.sort(
        key=lambda p: dt.datetime_from.string(
            get_date_str.__call__(p.stem), 
            fmt
        ),
        reverse=descending
    )
    return target_files


def get_most_recent_file(
    parent: StrPath,
    fmt: str,
    get_date_str: Optional[Callable[[str], str]]=None,
    target_ext: Optional[TargetExt]=None,
    filter_fn: Optional[Callable[[str], bool]]=None
) -> Path:
    """ 
    uses date in filename, not file's stat 
    """
    target_files = get_timesorted_files(
        parent, 
        fmt, 
        get_date_str, 
        target_ext, 
        True, 
        filter_fn
    )
    if not target_files:
        raise FileNotFoundError(LogMsg(
            f"No target files found under {parent=}",
            used_filter=bool(filter_fn),
            target_ext=str(target_ext)
        ))
    return target_files[0]

