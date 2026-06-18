"""Telegram Bot API ile bildirim gonderir."""
from __future__ import annotations

import time

import requests

from .config import Config

API = "https://api.telegram.org/bot{token}/sendMessage"


def send(config: Config, text: str, timeout: int = 20, retries: int = 3) -> None:
    """Telegram'a HTML formatli mesaj gonderir.

    Aglar gecici olarak kopabildigi icin birkac kez yeniden dener.
    Tum denemeler basarisiz olursa istisna firlatir.
    """
    payload = {
        "chat_id": config.telegram_chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }
    url = API.format(token=config.telegram_token)

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(url, data=payload, timeout=timeout)
            if resp.ok:
                return
            # 4xx (token/chat hatasi) tekrar denemeye degmez
            if 400 <= resp.status_code < 500:
                raise RuntimeError(
                    f"Telegram gonderimi reddedildi: {resp.status_code} {resp.text}"
                )
            last_error = RuntimeError(f"Telegram {resp.status_code}: {resp.text}")
        except requests.RequestException as exc:
            last_error = exc
        if attempt < retries:
            time.sleep(2 * attempt)  # artan bekleme

    raise RuntimeError(f"Telegram gonderimi {retries} denemede basarisiz: {last_error}")
