"""Bilinen notlari state.json'da saklar ve degisiklikleri (yeni/degisen not) hesaplar."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

from .obs import Grade

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "state.json")


@dataclass(frozen=True)
class Change:
    grade: Grade
    old_value: str | None  # None ise yeni ders, aksi halde onceki deger

    @property
    def is_new(self) -> bool:
        return self.old_value is None


def load(path: str = STATE_FILE) -> dict[str, dict]:
    """Onceki durumu okur: {ders_kodu: {"ders_adi":..., "value":...}}. Yoksa bos sozluk."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save(grades: list[Grade], path: str = STATE_FILE) -> None:
    data = {g.key: {"ders_adi": g.ders_adi, "value": g.value} for g in grades}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def diff(old: dict[str, dict], grades: list[Grade]) -> list[Change]:
    """Yeni eklenen veya degeri degisen dersleri dondurur."""
    changes: list[Change] = []
    for g in grades:
        prev = old.get(g.key)
        if prev is None:
            changes.append(Change(grade=g, old_value=None))
        elif prev.get("value") != g.value:
            changes.append(Change(grade=g, old_value=prev.get("value")))
    return changes
