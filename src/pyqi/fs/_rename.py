"""
*`@file`* `fs/_rename.py`
"""
from enum import auto
from pathlib import Path
from ._path import (to_path)
from .types import (StrPath, TargetExt, RenameOperation)
from ._search import (get_directory_files)
from lute import LogMsg
from typing import (Optional, Callable, Sequence, Mapping)
from .. import (_string as String, _array as Array)



def rename_dir_files(
    dir: StrPath,
    /,
    target_ext: Optional[TargetExt],
    how: RenameOperation,
    modifier: str,
    sep: str="_",
    recursive: bool=False, 
    fitler_fn: Optional[Callable[[str], bool]]=None
) -> list[Path]: 
    sep = sep or ""
    target_files = get_directory_files(
        dir, 
        target_ext, 
        recursive, 
        fitler_fn
    )
    return (
        rename_files(target_files, how=how, modifiers=modifier, sep=sep) 
        if target_files 
        else []
    )

def rename_files(
    files: StrPath | Sequence[StrPath] | Mapping[str, Path],
    /,
    how: RenameOperation,
    modifiers: Optional[str | Sequence[str]]=None,
    sep: str="_",
) -> list[Path]:
    sep = sep or ""
    if not isinstance(how, RenameOperation):
        raise TypeError(LogMsg(
            f"invalid param 'how: RenameOperation'",
            how=how,
            _sep=sep,
            files=files,
            modifiers=modifiers
        ))
    
    result: list[Path] = []
    if isinstance(files, (str, Path)): 
        path = to_path(files)
        modifier = modifiers if modifiers and isinstance(modifiers, str) else modifiers[0] if modifiers else ""
        new_path = _modify_filename(path, modifier, how, sep)
        if path != new_path:  path.rename(new_path)
        result.append(new_path)
    elif isinstance(files, Sequence):
        paths = Array.map(files, to_path)
        if modifiers and not isinstance(modifiers, str):
            for i, p in enumerate(paths):
                new_path = _modify_filename(p, modifiers[i], how, sep)
                result.append(new_path)
                if p != new_path: p.rename(new_path)
        else: # _raise_if_duplicate_paths
            seen: set[Path] = set()
            dupes: list[Path] = []
            for p in paths:
                if p in seen: dupes.append(p)
                else: seen.add(p)
            if dupes:
                raise ValueError(LogMsg(
                    f"Invalid argument 'files' when type(modifiers)=str",
                    dupes_preview=dupes[:5],
                    modifier=modifiers
                ))
            for i, p in enumerate(paths):
                new_path = _modify_filename(
                    p, 
                    (
                        modifiers if isinstance(modifiers, str) 
                        else modifiers[i] if modifiers 
                        else ""
                    ), 
                    how, 
                    sep
                )
                result.append(new_path)
                if p != new_path: p.rename(new_path)
    elif isinstance(files, Mapping):
        for mod, p in files.items():
            new_path = _modify_filename(p, mod, how, sep)
            result.append(new_path)
            if p != new_path: p.rename(new_path)
    else:
        raise TypeError(LogMsg(
            f"Invalid param 'files'",
            expected='StrPath | Sequence[StrPath] | Mapping[str, Path]',
            received=f"{type(files)=}"
        ))
    return result

def _modify_filename(
    path: Path,
    modifier: str,
    how: RenameOperation,
    sep: str
) -> Path: 
    suffix = "".join(path.suffixes)
    base = path.name[: -len(suffix)]
    new_name: str
    match how:
        case RenameOperation.PREPEND:
            if base.startswith(sep): sep = ""
            new_name = (
                f"{modifier}{sep}{base}{suffix}" if not base.startswith(modifier) 
                else f"{base}{suffix}"
            )
        case RenameOperation.APPEND:
            if base.endswith(sep): sep = ""
            new_name = (
                f"{base}{sep}{modifier}{suffix}" if not base.endswith(modifier)
                else f"{base}{suffix}"
            )
        case RenameOperation.REPLACE:
            new_name = f"{modifier}{suffix}"
        case _: # should be unreachable
            raise ValueError(LogMsg(f"Invalid param 'how: RenameOperation'"))
    return path.with_name(new_name)
