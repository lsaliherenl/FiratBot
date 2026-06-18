"""Bilinen notlari state.json'da saklar ve degisiklikleri (yeni/degisen not) hesaplar.

Gizlilik: repo public oldugu icin state.json'a ders adi/not gibi okunabilir bilgi
YAZILMAZ; sadece (ders + not) degerlerinin hash'leri tutulur. Bildirim metni canli
cekilen veriden uretilir, state'ten degil.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass

from .obs import Grade

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "state.json")


def _h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Change:
    grade: Grade
    is_new: bool  # True ise yeni ders, False ise notu degisen ders


def load(path: str = STATE_FILE) -> dict[str, str]:
    """Onceki durumu okur: {ders_kodu_hash: deger_hash}. Yoksa bos sozluk."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save(grades: list[Grade], path: str = STATE_FILE) -> None:
    data = {_h(g.key): _h(g.value) for g in grades}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def diff(old: dict[str, str], grades: list[Grade]) -> list[Change]:
    """Yeni eklenen veya degeri degisen dersleri dondurur."""
    changes: list[Change] = []
    for g in grades:
        kh = _h(g.key)
        if kh not in old:
            changes.append(Change(grade=g, is_new=True))
        elif old[kh] != _h(g.value):
            changes.append(Change(grade=g, is_new=False))
    return changes
