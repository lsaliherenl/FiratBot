"""Runner surecini yonetir: baslat/durdur/canli-mi + Startup kisayolu.

Hem dev (pythonw runner.py) hem paket (FiratBot.exe --run) durumlarini ele alir.
"""
from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
from ctypes import wintypes

from . import paths

_CREATE_NO_WINDOW = 0x08000000
_DETACHED_PROCESS = 0x00000008

_k32 = ctypes.windll.kernel32
_k32.OpenProcess.restype = wintypes.HANDLE
_k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]


def _project_dir() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def runner_command() -> list[str]:
    """Runner'i baslatan komut (paket vs dev)."""
    if is_frozen():
        return [sys.executable, "--run"]
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pyw):
        pyw = sys.executable
    return [pyw, os.path.join(_project_dir(), "runner.py")]


def read_status() -> dict:
    try:
        return json.loads(paths.STATUS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _pid_alive(pid: int) -> bool:
    if not pid:
        return False
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    handle = _k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
    if not handle:
        return False
    try:
        code = wintypes.DWORD()
        _k32.GetExitCodeProcess(handle, ctypes.byref(code))
        return code.value == STILL_ACTIVE
    finally:
        _k32.CloseHandle(handle)


def is_running() -> bool:
    return _pid_alive(read_status().get("pid", 0))


def start() -> bool:
    """Runner calismyorsa baslatir. True=baslatildi, False=zaten calisiyor."""
    if is_running():
        return False
    cmd = runner_command()
    subprocess.Popen(
        cmd,
        creationflags=_DETACHED_PROCESS | _CREATE_NO_WINDOW,
        cwd=None if is_frozen() else _project_dir(),
        close_fds=True,
    )
    return True


def stop() -> bool:
    """Calisan runner'i sonlandirir. True=durduruldu."""
    st = read_status()
    pid = st.get("pid", 0)
    if not _pid_alive(pid):
        return False
    subprocess.run(
        ["taskkill", "/PID", str(pid), "/F"],
        creationflags=_CREATE_NO_WINDOW,
        capture_output=True,
    )
    st["state"] = "stopped"
    try:
        paths.STATUS_FILE.write_text(
            json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        pass
    return True


def startup_lnk_path() -> str:
    return os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs\Startup",
        "FiratBot.lnk",
    )


def set_autostart(enabled: bool) -> None:
    """Oturum acilisinda otomatik baslamayi acar/kapar (Startup kisayolu)."""
    lnk = startup_lnk_path()
    if not enabled:
        try:
            os.remove(lnk)
        except FileNotFoundError:
            pass
        return
    cmd = runner_command()
    target = cmd[0]
    args = " ".join(f'"{a}"' if " " in a else a for a in cmd[1:])
    workdir = None if is_frozen() else _project_dir()
    ps = (
        "$ws=New-Object -ComObject WScript.Shell;"
        f"$l=$ws.CreateShortcut('{lnk}');"
        f"$l.TargetPath='{target}';"
        f"$l.Arguments='{args}';"
        + (f"$l.WorkingDirectory='{workdir}';" if workdir else "")
        + "$l.WindowStyle=7;$l.Save()"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps],
        creationflags=_CREATE_NO_WINDOW,
        capture_output=True,
    )
