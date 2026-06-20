"""Bilinen notlari state.json'da saklar ve degisiklikleri (yeni/degisen not) hesaplar.

Dosya yerel ve gitignore'da oldugu icin okunabilir deger saklanir; bu sayede
bildirimde eski->yeni gosterimi ve "sadece Final" filtresi mumkun olur.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from . import paths
from .obs import Grade


@dataclass
class Change:
    grade: Grade
    old: dict | None  # onceki kayit; None ise yeni ders

    @property
    def is_new(self) -> bool:
        return self.old is None

    @property
    def old_sinav_notlari(self) -> str:
        return (self.old or {}).get("sinav_notlari", "")


def load(path=None) -> dict[str, dict]:
    """Onceki durumu okur: {ders_kodu: {ders_adi, sinav_notlari, ..., value}}."""
    path = path or paths.STATE_FILE
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save(grades: list[Grade], path=None) -> None:
    path = path or paths.STATE_FILE
    paths.ensure_app_dir()
    data = {
        g.key: {
            "ders_adi": g.ders_adi,
            "sinav_notlari": g.sinav_notlari,
            "ortalama": g.ortalama,
            "harf_notu": g.harf_notu,
            "durum": g.durum,
            "value": g.value,
        }
        for g in grades
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def diff(old: dict[str, dict], grades: list[Grade]) -> list[Change]:
    """Yeni eklenen veya degeri degisen dersleri dondurur."""
    changes: list[Change] = []
    for g in grades:
        prev = old.get(g.key)
        if prev is None:
            changes.append(Change(grade=g, old=None))
        elif prev.get("value") != g.value:
            changes.append(Change(grade=g, old=prev))
    return changes
