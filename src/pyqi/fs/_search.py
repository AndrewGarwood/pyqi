"""
*`@file`* `fs/_search.py`
""" 
import os
from pathlib import Path
from typing import (Callable)
from lute import LogMsg, annotate
from .types import (StrPath, TargetExt)
from ._path import (to_path, has_target_ext, normalize_ext_input)
from .. import (_array as Array, _dt as dt)
from ..utils.module import export

def get_directory_files(
    dir: StrPath, 
    target_ext: TargetExt | None=None, 
    recursive: bool=False, 
    filter_fn: Callable[[str], bool] | None=None
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
    target_ext: TargetExt | None=None, 
    recursive: bool=False, 
    filter_fn: Callable[[str], bool] | None=None,
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
    filter_fn: Callable[[str], bool] | None=None,
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

def get_child_directories(
    parent: StrPath,
    /,
    filter_fn: Callable[[str], bool] | None=None,
) -> list[Path]:
    """
    *`@note`* only gets direct descendant of parent for now. i.e. no grandchildren
    """
    parent = to_path(parent)
    target_dirs: list[str] = []
    walk = tuple(os.walk(parent))
    walk_limit = 1 # min(1, len(walk)) if not recursive else len(walk)
    for i in range(walk_limit):
        (_, dirs, _) = walk[i]
        _target_dirs = dirs
        if filter_fn:
            _target_dirs = Array.filter(dirs, filter_fn)
        target_dirs.extend(_target_dirs)
    return Array.map(target_dirs, lambda x: parent.joinpath(x))


#TODO: maybe try rm fmt as param of the timesorted functions and use dateutil parse instead
# or require/assume that filter_fn handles narrowing to dated paths 

def get_most_recent_dir(
    parent: StrPath,
    /,
    get_date_str: Callable[[str], str]=lambda x: x[:10],
    filter_fn: Callable[[str], bool] | None=None,
) -> Path:
    return get_timesorted_directories(
        parent, 
        get_date_str=get_date_str, 
        filter_fn=filter_fn, 
        descending=True
    )[0]

def get_timesorted_directories(
    parent: StrPath,
    /,
    get_date_str: Callable[[str], str]=lambda x: x[:10],
    filter_fn: Callable[[str], bool] | None=None,
    descending: bool=True,
) -> list[Path]:
    parent = to_path(parent)
    dated_dirs: list[tuple[Path, dt.date]] = []
    walk = list(os.walk(parent))
    walk_limit = 1
    for i in range(walk_limit):
        (root, dirs, _) = walk[i]
        for d in dirs:
            if filter_fn and not filter_fn(d): continue
            try:
                dated_dirs.append((
                    parent.joinpath(d), 
                    dt.date_from.pathstem(d, get_date_part=get_date_str)
                ))
            except Exception: pass
    if not dated_dirs:
        raise RuntimeError(LogMsg(
            "No dated dirs found under parent", 
            parent=str(parent)
        ))
    dated_dirs.sort(key=lambda tup: tup[1], reverse=descending)
    return Array.map(dated_dirs, lambda tup: tup[0])


def get_timesorted_files(
    parent: StrPath,
    /,
    get_date_str: Callable[[str], str] | None=None,
    target_ext: TargetExt | None=None,
    descending: bool=True,
    filter_fn: Callable[[str], bool] | None=None
) -> list[Path]:
    target_ext = normalize_ext_input(target_ext) if target_ext else []
    target_files = get_directory_files(
        parent, 
        target_ext, 
        False, 
        filter_fn
    )
    get_date_str = (
        (lambda s: s.split("_", 1)[0]) if get_date_str is None 
        else get_date_str
    )
    dated_files: list[tuple[Path, dt.date]] = []
    for f in target_files:
        try:
            _d = dt.date_from.pathstem(f.stem, get_date_part=get_date_str)
            dated_files.append((f, _d))
        except Exception:
            pass
    if not dated_files:
        raise RuntimeError(LogMsg(
            f"No dated files found under {parent=}",
            filter_fn=annotate(filter_fn),
            target_ext=str(target_ext),
            target_files=str(target_files),
            dated_files=str(dated_files)
        ))

    dated_files.sort(
        key=lambda tup: tup[1],
        reverse=descending
    )
    return Array.map(dated_files, lambda tup: tup[0])


def get_most_recent_file(
    parent: StrPath,
    get_date_str: Callable[[str], str] | None=None,
    target_ext: TargetExt | None=None,
    filter_fn: Callable[[str], bool] | None=None
) -> Path:
    """ 
    uses date in filename, not file's stat 
    """
    target_files = get_timesorted_files(
        parent, 
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

__all__ = export(
    get_directory_files, 
    find_file, 
    find_dir, 
    get_child_directories, 
    get_timesorted_directories, 
    get_timesorted_files, 
    get_most_recent_file
)