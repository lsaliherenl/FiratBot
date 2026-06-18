"""Gelistirme yardimcisi: girisi test eder ve cekilen notlari ekrana basar.

Kullanim:
    python debug_login.py            # headless
    python debug_login.py --show     # tarayiciyi gorunur calistir (hata ayiklama)

Telegram gerektirmez; sadece FIRAT_USERNAME / FIRAT_PASSWORD okur.
"""
from __future__ import annotations

import sys

from firatbot.config import Config, ConfigError
from firatbot.obs import fetch_grades


def main(argv: list[str]) -> int:
    show = "--show" in argv
    try:
        config = Config.load_firat_only()
    except ConfigError as exc:
        print(f"[HATA] {exc}")
        return 1

    print(f"Giris ve not cekme deneniyor: {config.firat_username} ...")
    try:
        grades = fetch_grades(config, headless=not show)
    except Exception as exc:  # noqa: BLE001 - debug araci
        print(f"[HATA] {exc}")
        return 1

    print(f"[OK] {len(grades)} ders bulundu:\n")
    for g in grades:
        print(f"  {g.ders_kodu:8s} {g.ders_adi[:35]:35s} | {g.sinav_notlari}  [{g.durum}]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
