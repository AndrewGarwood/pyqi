"""
*`@file`* `fs/_dir.py`
"""
import time, shutil
from lute import get_logger
from ._path import *

mlog = get_logger(Path(__file__).parent.stem)

def ensure_dir_exists(path: StrPath, /, parents=True, exist_ok=True) -> bool:
    """ 
    `if not is_dir(path): path.mkdir(parents=parents, exist_ok=exist_ok)` 
    - *`@returns`* `created (bool)` whether dir was made or not
    """
    path = to_path(path)
    created = not is_dir(path)
    if created:
        path.mkdir(parents=parents, exist_ok=exist_ok)
    return created

def dir_is_writable(
    path: StrPath, 
    /,
    mkdir: bool=True
) -> bool: 
    """
    @param `path (Path)` filepath to derive parent or parent dir itself
    """
    try:
        path = to_path(path)
        _dir = path if path.is_dir() else path.parent
        if mkdir:
            ensure_dir_exists(_dir)
        elif not is_dir(_dir):
            raise FileNotFoundError(LogMsg(
                f"Directory does not exist",
                _dir=_dir,
            ))
        test_path = (
            path.joinpath("fs.write_test.tmp") if path.is_dir() 
            else path.with_name(f"{path.stem}.write_test.tmp")
        )
        try:
            test_path.write_text("test", encoding="utf-8")
            test_path.unlink()
            return True
        except Exception as e:
            raise PermissionError(LogMsg(
                f"({type(e)}) Cannot write to output directory: {_dir}", 
                error=str(e)
            )) from e
    except Exception as e:
        mlog.warning(LogMsg.err(
            error=e,
            is_permission_error=isinstance(e, PermissionError),
            path=str(path),
            mkdir=mkdir
        ))
        return False


def empty_dir(dir: StrPath, /):
    dir = to_path(dir)
    if (not dir.is_dir()): 
        return False
    for item in dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else: 
            item.unlink()
    time.sleep(1)
    return (not os.listdir(dir))


def size_of_dir(dir: StrPath, /) -> int:
    try:
        dir = to_path(dir)
        if (not dir.is_dir()): 
            raise ValueError(f"Provided path is not a directory")
        return sum(
            p.stat().st_size
            for p in dir.rglob("*")
            if p.is_file()
        )
    except Exception as e:
        raise Exception(LogMsg.err(
            error=e,
            dir=str(dir)
        )) from e

    
def copy_dir(
    src: StrPath, 
    dst_parent: Optional[StrPath]=None,
    /,
    name: Optional[str]=None,
    copy_suffix: str = " - Copy({i})"
) -> Path:
    src = to_path(src)
    dst_parent = to_path(dst_parent) if dst_parent else src.parent
    name = name or src.name
    target = dst_parent.joinpath(name)
    if target.exists():
        i = 1
        while True:
            candidate = dst_parent.joinpath(f"{name}{copy_suffix.format(i)}")
            if not candidate.exists():
                target = candidate
                break
            i += 1
    shutil.copytree(src, target)
    return target