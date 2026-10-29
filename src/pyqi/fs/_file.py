"""
*`@file`* `fs/_file.py`
"""
import time, shutil, tempfile
from pathlib import Path
from datetime import datetime
from lute import get_logger
from ._dir import (ensure_dir_exists)
from ._path import (StrPath, to_path, is_file)
from lute import LogMsg
from .. import _array as Array


mlog = get_logger(Path(__file__).parent.stem)

def wait_for_file_unlock(
    path: StrPath,
    /,
    timeout_seconds: float = 60.0,
    poll_seconds: float = 0.25,
) -> None:
    path = to_path(path)
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with path.open("rb+"): return
        except Exception as e:
            last_error = e
            time.sleep(poll_seconds)
    raise TimeoutError(LogMsg(
        f"File did not become unlocked",
        last_error_str=str(last_error),
        path=str(path)
    )) from last_error

def wait_for_file_exists(
    path: StrPath,
    /,
    timeout: float = 60.0,
    poll: float = 0.25,
    stable_checks: int = 3,
) -> Path:
    """
    i.e. `is_stable_after_wait`
    Wait until file exists and size stabilizes for a few polls.
    """
    p = Path(path)
    deadline = time.time() + timeout
    stable = 0
    last_size = -1
    while time.time() < deadline:
        if p.exists():
            size = p.stat().st_size
            if size > 0 and size == last_size:
                stable += 1
                if stable >= stable_checks:
                    return p
            else:
                stable = 0
                last_size = size
        time.sleep(poll)
    raise TimeoutError(f"Timed out waiting for file: {p}")


def make_temp_file(src: StrPath, dst: StrPath, stem_suffix: str=".tmp") -> Path:
    tmppath: Path | None
    try:
        src = to_path(src)
        if not is_file(src):
            raise FileNotFoundError(f"{src.name} does not exist at given path")
        dst = to_path(dst)
        dst.mkdir(parents=True, exist_ok=True)
        tmppath = dst.joinpath(f"{src.stem}{stem_suffix}{src.suffix}")
        tmpfile = tempfile.NamedTemporaryFile(
            dir=dst, 
            prefix=f"{src.stem}{stem_suffix}",
            suffix=src.suffix,
            delete=False
        )
        tmpfile.close()
        shutil.copy2(src, tmppath)
        return tmppath
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            error=e,
            original=str(src),
            oudir=str(dst),
        )) from e


def copy_file(
    src: StrPath, 
    dst: StrPath | None=None,
    /,
    overwrite: bool=False
) -> Path:
    """
    - *`@param`* `dst` can be filepath or dirpath, resolves to filepath
    - wrapper for `shutil.copy2()`
    - *`@returns`* `dst (Path)` resolved dst filepath
    """
    try:
        src = to_path(src)
        if not is_file(src):
            raise FileNotFoundError(f"{src.name} does not exist at given path")
        if dst is None:
            dst = src.with_stem(f"{src.stem}_{datetime.now().isoformat()}")
        else:
            dst = Path(dst)
            dst = dst.joinpath(src.name) if dst.is_dir() else dst
        
        if is_file(dst):
            if overwrite:
                dst.unlink()
            else:
                raise FileExistsError(f"{dst.name=} already exists in dir {dst.parent=}")
        shutil.copy2(src=src, dst=dst)
        return dst
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e, 
            original=src, 
            outpath=dst, 
            overwrite=overwrite
        )) from e

def stage_file(
    src: StrPath, 
    /, 
    dst: StrPath,
    overwrite: bool=False
) -> Path:
    """
    *`@param`* `dst (StrPath)` - can be filepath or dirpath
    """
    try:
        src = to_path(src)
        wait_for_file_unlock(src)
        dst = to_path(dst)
        if dst.is_dir():
            dst = dst.joinpath(f"{src.stem}.staged{src.suffix}")
        ensure_dir_exists(dst.parent)
        copy_file(src, dst, overwrite=overwrite)
        wait_for_file_unlock(dst)
        return dst
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            error=e, 
            src=str(src), 
            dst=str(dst), 
            overwrite=overwrite
        ))


def publish_staged_file(
    src: StrPath, 
    /, 
    *dst: StrPath,
    backup_existing: bool=True,
    backup_dir: StrPath | None=None
) -> list[Path]:
    published: list[Path] = []
    try:
        src = to_path(src)
        wait_for_file_unlock(src)
        for p in Array.map(dst, to_path):
            _dstfile: Path = p.joinpath(src.name) if p.is_dir() else p
            if (p.is_file() and backup_existing):
                wait_for_file_unlock(p)
                new_parent = Path(backup_dir) if backup_dir else p.parent
                backup_path = new_parent.joinpath(
                    f"{p.stem}.backup.{time.strftime('%Y%m%d_%H%M%S')}{p.suffix}"
                )
                p.replace(backup_path)
            p.unlink(missing_ok=True)
            ensure_dir_exists(_dstfile.parent)
            published.append(copy_file(src, _dstfile))
        return published
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e,
            src=str(src),
            dst=str(dst),
            backup_dir=str(backup_dir)
        )) from e

def size_of_file(path: StrPath, /) -> int:
    return to_path(path).stat().st_size