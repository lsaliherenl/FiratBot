"""Telegram chat ID bulma yardimcisi.

Kullanim:
    1. BotFather'dan aldigin token'i .env icindeki TELEGRAM_TOKEN'a yaz.
    2. Telegram'da botunu bul ve ona herhangi bir mesaj at (orn. /start veya "merhaba").
    3. python get_chat_id.py

Cikan chat ID'yi .env icindeki TELEGRAM_CHAT_ID'ye yaz.
"""
from __future__ import annotations

import os
import sys

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def main() -> int:
    token = os.environ.get("TELEGRAM_TOKEN", "").strip()
    if not token:
        print("[HATA] TELEGRAM_TOKEN tanimli degil. Once .env'e token'i yaz.")
        return 1

    resp = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20)
    data = resp.json()
    if not data.get("ok"):
        print(f"[HATA] Telegram yaniti: {data}")
        return 1

    results = data.get("result", [])
    if not results:
        print(
            "Hic mesaj bulunamadi. Once Telegram'da botuna bir mesaj at (orn. /start), "
            "sonra bu scripti tekrar calistir."
        )
        return 1

    seen = {}
    for upd in results:
        msg = upd.get("message") or upd.get("edited_message") or {}
        chat = msg.get("chat") or {}
        if chat.get("id") is not None:
            seen[chat["id"]] = chat.get("username") or chat.get("first_name") or "?"

    print("Bulunan chat ID'ler:")
    for cid, name in seen.items():
        print(f"  chat_id = {cid}   ({name})")
    print("\nBu degeri .env -> TELEGRAM_CHAT_ID ve GitHub Secrets'a yaz.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
