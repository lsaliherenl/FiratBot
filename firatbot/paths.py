"""FiratBot calisma dosyalarinin yollari (tek yerde).

Ayarlar/loglar exe nereden calisirsa calissin yazilabilir, sabit bir konumda
tutulur: %APPDATA%\\FiratBot\\
"""
from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(os.environ.get("APPDATA") or Path.home()) / "FiratBot"

SETTINGS_FILE = APP_DIR / "settings.json"
STATE_FILE = APP_DIR / "state.json"
LOG_FILE = APP_DIR / "loop.log"
STATUS_FILE = APP_DIR / "status.json"


def ensure_app_dir() -> Path:
    """Uygulama klasorunu olusturur (yoksa) ve dondurur."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    return APP_DIR
