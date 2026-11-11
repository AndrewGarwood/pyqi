"""
*`@file`* `fs/_archive`
"""
from pathlib import Path
from ._path import (StrPath, to_path, lname)
from ._dir import (ensure_dir_exists)
from ._stat import format_bytestr, size_of_dir
from pyqi.utils.module import export
from .types import ArchiveFormat
import shutil
from lute import LogMsg, get_logger

mlog = get_logger(__file__, name_depth=1)

def archive_stem(path: StrPath) -> Path:
    """ 
    *`@returns`* `path` without archive suffix (`assuming path.name.lower()` is some `ArchiveFormat` value)
    """
    path = to_path(path)
    for fmt in sorted(
        ArchiveFormat,
        key=lambda fmt: len(fmt),
        reverse=True,
    ):
        if path.name.lower().endswith(fmt):
            return path.with_name(path.name[:-len(fmt)])
    return path


def extract_archive(
    src: StrPath,
    dst: StrPath | None=None,
    /,
    *,
    overwrite: bool=False,
    verbose: bool=True
) -> Path:
    """
    if `dst is None`: derive dst from src.stem
        - report.zip -> report/
    """
    try:
        src = to_path(src)
        if not src.exists():
            raise FileNotFoundError(f"src path does not exist")
        dst = archive_stem(src) if dst is None else to_path(dst)
        if dst.exists() and not overwrite:
            raise FileExistsError(f"dst path exists & {overwrite=}")
        ensure_dir_exists(dst)
        shutil.unpack_archive(filename=str(src).lower(), extract_dir=str(dst))
        if verbose:
            archive_size_bytes = src.stat().st_size
            extracted_size_bytes = size_of_dir(dst)
            compression_ratio = (extracted_size_bytes / archive_size_bytes
                if archive_size_bytes > 0
                else float("nan")
            )
            mlog.info(LogMsg(
                f"Finished:",
                f"Extracted {lname(src)} → {lname(dst)}",
                src_size_bytes=f"{archive_size_bytes} ({format_bytestr(archive_size_bytes)})",
                dst_size_bytes=f"{extracted_size_bytes} ({format_bytestr(extracted_size_bytes)})",
                compression_ratio=f"{compression_ratio:.2f}"
            ))
        return dst
    except Exception as e:
        raise RuntimeError(LogMsg.err(e,
            src=str(src),
            dst=str(dst)
        )) from e

__all__ = export(archive_stem, extract_archive)