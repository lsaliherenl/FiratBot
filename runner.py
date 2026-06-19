"""FiratBot surekli dongu - her 15 dakikada bir not kontrolu yapar.

Oturum acilisinda (Startup) gizli olarak baslatilir ve interaktif oturum
baglaminda calisir (Gorev Zamanlayici'nin kisitli baglami Playwright tarayicisini
bulamadigi icin bu yontem tercih edildi).

Ciktilar loop.log'a yazilir. pythonw ile penceresiz calisir.
"""
from __future__ import annotations

import datetime
import os
import sys
import time

# Calisma dizinini bu dosyanin klasorune sabitle (.env ve modul yollari icin)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Tarayici yolunu garanti altina al (bazi baslangic baglamlarinda gerekebilir)
_default_browsers = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local")), "ms-playwright"
)
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", _default_browsers)

# Tum ciktilari (kendi + check.py) loop.log'a yonlendir (pythonw'da stdout yoktur)
_log = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "loop.log"), "a", encoding="utf-8", buffering=1)
sys.stdout = _log
sys.stderr = _log

from check import main as check_main  # noqa: E402

INTERVAL_SEC = 15 * 60


def _ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def loop() -> None:
    print(f"[{_ts()}] === FiratBot dongu basladi (her {INTERVAL_SEC // 60} dk) ===", flush=True)
    while True:
        print(f"[{_ts()}] kontrol calisiyor...", flush=True)
        try:
            check_main([])
        except Exception as exc:  # noqa: BLE001 - dongu asla olmesin
            print(f"[{_ts()}] [HATA] dongu hatasi: {exc!r}", flush=True)
        print(f"[{_ts()}] {INTERVAL_SEC // 60} dk uyku.\n", flush=True)
        time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    try:
        loop()
    except KeyboardInterrupt:
        print(f"[{_ts()}] dongu durduruldu.", flush=True)
