"""Telegram Bot API ile bildirim gonderir."""
from __future__ import annotations

import requests

from .config import Config

API = "https://api.telegram.org/bot{token}/sendMessage"


def send(config: Config, text: str, timeout: int = 20) -> None:
    """Telegram'a HTML formatli mesaj gonderir. Hata olursa istisna firlatir."""
    resp = requests.post(
        API.format(token=config.telegram_token),
        data={
            "chat_id": config.telegram_chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        },
        timeout=timeout,
    )
    if not resp.ok:
        raise RuntimeError(f"Telegram gonderimi basarisiz: {resp.status_code} {resp.text}")
