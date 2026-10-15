"""
*`@file`* `fs/_process.py`
"""

from pathlib import Path
import psutil,subprocess
from lute import (get_logger, LogMsg)
from ._path import to_path
from .types import (StrPath)

mlog = get_logger(Path(__file__).parent.stem)

def kill_procs(procs: list[psutil.Process], /, timeout: float=5.0):
    terminated: list[psutil.Process] = []
    for p in procs:
        try:
            if p.is_running():
                p.terminate()
                p.wait(timeout=timeout)
                terminated.append(p)
        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
            OSError,
        ) as e:
            print(LogMsg.err(error=e))
            continue
    return terminated

def terminate_process_instances(exepath: StrPath, /) -> int:
    """ terminates then kills"""
    exepath = to_path(exepath)
    terminated: list[psutil.Process] = []
    for p in psutil.process_iter(["pid", "exe"]):
        try:
            exe = p.info["exe"]
            if not exe:
                continue
            if to_path(exe) == exepath:
                p.terminate()
                terminated.append(p)
            
        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
            OSError,
            Exception,
        ) as e:
            mlog.warning(LogMsg(
                f"Encountered error during psutil.process_iter",
                error=str(e),
                exepath=str(exepath)
            ))
            continue
    _, alive = psutil.wait_procs(terminated, timeout=10.0)
    if len(alive):
        mlog.info(LogMsg(f"Attempting Process.kill() for {len(alive)} proc(s) in alive"))
        kill_procs(alive)
    return len(terminated)

def launch_executable(exepath: StrPath, /, terminate_existing: bool=True) -> bool:
    """
    Launch an executable `(.exe)` if it is not already 
    running with `subprocess.Popen([str(exepath)])`
    
    Returns
    -------
    bool
        - `True` if a new process was launched.
        - `False` if the executable was already running and `terminate_existing = False`.
    """
    exepath = to_path(exepath)
    if exepath.suffix.lower() != '.exe':
        raise ValueError(f"Invalid argument 'exepath' - does not have .exe extension")
    count: int = 0
    if terminate_existing:
        count = terminate_process_instances(exepath)
        print(f" > closed {count} instance(s) of {exepath.name}")
    else:
        for proc in psutil.process_iter(["exe"]):
            try:
                proc_exe = proc.info["exe"]
                if not proc_exe:
                    continue
                if to_path(str(proc_exe)) == exepath:
                    return False
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
                OSError,
                Exception,
            ) as e:
                print(LogMsg(
                    f"Encountered error during psutil.process_iter",
                    error=str(e),
                    exepath=str(exepath)
                ))
                continue
    subprocess.Popen([str(exepath)])
    return True

def start_process(exepath: StrPath, /, terminate_existing: bool=True) -> int:
    # TODO: launch then return pid
    raise NotImplementedError()
    # return launch_executable(exepath, terminate_existing)