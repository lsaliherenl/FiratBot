"""Surekli dongu: her N dakikada bir not kontrolu (N = settings.interval_minutes).

Hem yerelde (pythonw runner.py) hem de pakette (FiratBot.exe --run) ayni
run_loop() cagrilir. Ciktilar paths.LOG_FILE'a, durum paths.STATUS_FILE'a yazilir.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
import time

from . import paths, settings


def _ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _write_status(**kw) -> None:
    paths.ensure_app_dir()
    data = {"pid": os.getpid(), "updated": _ts(), **kw}
    try:
        paths.STATUS_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        pass


def run_loop() -> None:
    paths.ensure_app_dir()
    log = open(paths.LOG_FILE, "a", encoding="utf-8", buffering=1)
    sys.stdout = log
    sys.stderr = log

    from check import main as check_main  # noqa: E402

    print(f"[{_ts()}] === FiratBot dongu basladi ===", flush=True)
    _write_status(state="running", last_run=None, last_result=None)

    while True:
        s = settings.load()
        interval = max(1, int(s.interval_minutes)) * 60
        print(f"[{_ts()}] kontrol calisiyor (filtre={s.notify_filter})...", flush=True)
        try:
            rc = check_main([])
            result = "ok" if rc == 0 else f"rc={rc}"
        except Exception as exc:  # noqa: BLE001 - dongu asla olmesin
            result = f"hata: {exc!r}"
            print(f"[{_ts()}] [HATA] dongu hatasi: {exc!r}", flush=True)
        _write_status(
            state="running",
            last_run=_ts(),
            last_result=result,
            interval_minutes=s.interval_minutes,
        )
        print(f"[{_ts()}] {interval // 60} dk uyku.\n", flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    try:
        run_loop()
    except KeyboardInterrupt:
        pass
