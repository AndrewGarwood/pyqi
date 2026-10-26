"""
*`@file`* `io/text`
"""
from pathlib import Path
from typing import Any, Callable, Iterable, TypeVar, TypeAlias
from lute import LogMsg, annotate

T = TypeVar('T')

StrPath: TypeAlias = str | Path

def read_list(
    path: StrPath, 
    /, 
    sep: str = "\n", 
    encoding: str = "utf-8",
    normalize: Callable[[str], T] = lambda x: x.strip(),
) -> list[T]:
    """
    - *`@note`* if an `item` is empty string, it is *not* normalized/added to result list
        - where `item` is element in `f.read().strip().split(sep)`
    """
    try:
        result: list[T] = []
        with Path(path).open('r', encoding=encoding) as f:
            data = f.read().strip()
            for item in data.split(sep):
                if not item: continue
                result.append(normalize(item))
        return result
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e, 
            f"Failed to read list from file content",
            path=str(path),
            sep_char=sep,
            normalize_fn=annotate(normalize)
        )) from e


def write_list(
    data: Iterable[Any],
    path: StrPath,
    /,
    sep: str = "\n",
    ext: str = ".txt",
    normalize: Callable[[T], str] = str,
):
    """
    *`@note`* writes to `Path(path).with_suffix(ext)`
    - does not check if path already exists.
    - writes `'{normalize(item)}{sep}'` for `item` in `data`
    """
    try:
        path = Path(path).with_suffix(ext)
        with path.open("w") as f:
            for item in data:
                f.write(f"{normalize(item)}{sep}")
        return path
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e,
            f"Failed to write data to output path",
            path=str(path),
            data=annotate(data),
            sep_char=sep,
            normalize_fn=annotate(normalize)
        )) from e