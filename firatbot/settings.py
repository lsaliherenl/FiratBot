"""settings.json yonetimi: oku/yaz, sirlari DPAPI ile sifrele/coz, .env'den ilk goc.

Bellekte sirlar DUZ METIN (Settings alanlari); diske yazarken sifrelenir.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass

from . import paths, secretstore

NOTIFY_FILTERS = ("all", "final_only")


@dataclass
class Settings:
    firat_username: str = ""
    firat_password: str = ""        # bellekte duz metin; diske *_enc olarak yazilir
    telegram_token: str = ""        # bellekte duz metin; diske *_enc olarak yazilir
    telegram_chat_id: str = ""
    interval_minutes: int = 15
    notify_filter: str = "all"      # "all" | "final_only"
    autostart: bool = True


def _decrypt(value: str) -> str:
    if not value:
        return ""
    try:
        return secretstore.unprotect(value)
    except OSError:
        return ""


def _to_disk(s: Settings) -> dict:
    return {
        "firat_username": s.firat_username,
        "firat_password_enc": secretstore.protect(s.firat_password) if s.firat_password else "",
        "telegram_token_enc": secretstore.protect(s.telegram_token) if s.telegram_token else "",
        "telegram_chat_id": s.telegram_chat_id,
        "interval_minutes": int(s.interval_minutes),
        "notify_filter": s.notify_filter if s.notify_filter in NOTIFY_FILTERS else "all",
        "autostart": bool(s.autostart),
    }


def _from_disk(data: dict) -> Settings:
    return Settings(
        firat_username=str(data.get("firat_username", "")),
        firat_password=_decrypt(data.get("firat_password_enc", "")),
        telegram_token=_decrypt(data.get("telegram_token_enc", "")),
        telegram_chat_id=str(data.get("telegram_chat_id", "")),
        interval_minutes=int(data.get("interval_minutes", 15) or 15),
        notify_filter=data.get("notify_filter", "all"),
        autostart=bool(data.get("autostart", True)),
    )


def _migrate_from_env() -> Settings:
    """settings.json yoksa, mevcut .env / ortam degiskenlerinden ilk degerleri al."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    return Settings(
        firat_username=os.environ.get("FIRAT_USERNAME", "").strip(),
        firat_password=os.environ.get("FIRAT_PASSWORD", "").strip(),
        telegram_token=os.environ.get("TELEGRAM_TOKEN", "").strip(),
        telegram_chat_id=os.environ.get("TELEGRAM_CHAT_ID", "").strip(),
    )


def load() -> Settings:
    """Ayarlari okur. settings.json yoksa .env'den goc edip kaydeder."""
    paths.ensure_app_dir()
    if paths.SETTINGS_FILE.exists():
        try:
            data = json.loads(paths.SETTINGS_FILE.read_text(encoding="utf-8"))
            return _from_disk(data)
        except (json.JSONDecodeError, OSError):
            return Settings()
    # Ilk calistirma: .env'den goc
    migrated = _migrate_from_env()
    try:
        save(migrated)
    except OSError:
        pass
    return migrated


def save(s: Settings) -> None:
    paths.ensure_app_dir()
    paths.SETTINGS_FILE.write_text(
        json.dumps(_to_disk(s), ensure_ascii=False, indent=2), encoding="utf-8"
    )
