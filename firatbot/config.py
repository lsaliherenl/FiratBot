"""Ortam degiskenlerinden yapilandirma okur.

Yerelde `.env` dosyasi, cloud'da (GitHub Actions) ortam degiskeni / Secrets kullanilir.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv kurulu degilse ortam degiskenlerine guveniriz
    pass


class ConfigError(RuntimeError):
    """Eksik/hatali yapilandirma."""


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(
            f"'{name}' ortam degiskeni tanimli degil. "
            f".env dosyasini doldurun (bkz. .env.example) veya Secrets ekleyin."
        )
    return value


@dataclass(frozen=True)
class Config:
    firat_username: str
    firat_password: str
    telegram_token: str
    telegram_chat_id: str

    @classmethod
    def load(cls) -> "Config":
        return cls(
            firat_username=_require("FIRAT_USERNAME"),
            firat_password=_require("FIRAT_PASSWORD"),
            telegram_token=_require("TELEGRAM_TOKEN"),
            telegram_chat_id=_require("TELEGRAM_CHAT_ID"),
        )

    @classmethod
    def load_firat_only(cls) -> "Config":
        """Telegram olmadan sadece OBS girisini test etmek icin (debug)."""
        return cls(
            firat_username=_require("FIRAT_USERNAME"),
            firat_password=_require("FIRAT_PASSWORD"),
            telegram_token=os.environ.get("TELEGRAM_TOKEN", ""),
            telegram_chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
        )
