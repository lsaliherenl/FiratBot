"""Calisma yapilandirmasi. Kaynak: settings.json (GUI ile yonetilir).

settings.json yoksa, settings.load() otomatik olarak .env / ortam degiskenlerinden
goc eder (geriye uyum).
"""
from __future__ import annotations

from dataclasses import dataclass

from . import settings as _settings


class ConfigError(RuntimeError):
    """Eksik/hatali yapilandirma."""


@dataclass(frozen=True)
class Config:
    firat_username: str
    firat_password: str
    telegram_token: str
    telegram_chat_id: str
    interval_minutes: int = 15
    notify_filter: str = "all"

    @classmethod
    def load(cls) -> "Config":
        s = _settings.load()
        return cls(
            firat_username=s.firat_username,
            firat_password=s.firat_password,
            telegram_token=s.telegram_token,
            telegram_chat_id=s.telegram_chat_id,
            interval_minutes=s.interval_minutes,
            notify_filter=s.notify_filter,
        )

    # Geriye uyum: eski cagrilar load_firat_only kullaniyordu
    load_firat_only = load

    def require_firat(self) -> None:
        if not self.firat_username or not self.firat_password:
            raise ConfigError(
                "OBS kullanici adi/parola tanimli degil. Ayar penceresinden girin."
            )

    def require_telegram(self) -> None:
        if not self.telegram_token or not self.telegram_chat_id:
            raise ConfigError(
                "Telegram token/chat ID tanimli degil. Ayar penceresinden girin."
            )
