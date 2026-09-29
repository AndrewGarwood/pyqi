"""
*`@file`* `_json/write`
"""
import json
from pathlib import (Path)
from typing import Optional, TypeAlias
from lute import (LogMsg, annotate)
from .types import (JsonValue)


StrPath: TypeAlias = str | Path
def file(
    data: JsonValue, 
    path: StrPath, 
    /,
    indent: Optional[int]=4, 
    **kwargs
) -> Path:
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as f:
            json.dump(data,f, indent=indent, **kwargs)
        return path
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e, 
            path=annotate(path),
            data=f'{type(data)}',
            kwargs=str(kwargs)
        )) from e

def dumpstr(data: JsonValue, /, indent: Optional[int]=4, **kwargs):
    try:
        return json.dumps(data, indent=indent, **kwargs)
    except Exception as e:
        raise RuntimeError(LogMsg.err(
            e,
            data=f"{type(data)}",
            kwargs=str(kwargs)
        )) from e