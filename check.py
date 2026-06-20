"""FiratBot tek kontrol: giris -> notlari cek -> degisiklik -> bildir -> state guncelle.

Tek seferlik calisir ve cikar. Surekli calismayi runner.py saglar.

Kullanim:
    python check.py
    python check.py --no-notify   # bildirim gondermeden (yerel test)
"""
from __future__ import annotations

import html
import re
import sys

from firatbot import state
from firatbot.config import Config, ConfigError
from firatbot.notifier import send
from firatbot.obs import Grade, fetch_grades

_EXAM_RE = re.compile(r"([A-Za-zÇĞİÖŞÜçğıöşü.]+)\s*:\s*(\S+)")


def _parse_exams(sinav_notlari: str) -> dict[str, str]:
    """'Vize : 65 Final : 70' -> {'Vize':'65','Final':'70'}."""
    return {m.group(1): m.group(2) for m in _EXAM_RE.finditer(sinav_notlari or "")}


def _final_changed(old_notlari: str, new_notlari: str) -> bool:
    """Final notu gercek bir sayiya donmus/degismis mi?"""
    new_final = _parse_exams(new_notlari).get("Final")
    old_final = _parse_exams(old_notlari).get("Final")
    return new_final is not None and new_final not in ("--", "") and new_final != old_final


def _apply_filter(changes: list[state.Change], notify_filter: str) -> list[state.Change]:
    if notify_filter == "final_only":
        return [c for c in changes if _final_changed(c.old_sinav_notlari, c.grade.sinav_notlari)]
    return changes


def _format_change(change: state.Change) -> str:
    g = change.grade
    ders = html.escape(g.ders_adi)
    yeni = html.escape(g.sinav_notlari or "-")
    durum = html.escape(g.durum or "-")
    baslik = "🆕 Yeni ders/not" if change.is_new else "📢 Not güncellendi"
    satir = f"<b>{baslik}</b>\n📚 {ders}\n📝 {yeni}"
    onceki = change.old_sinav_notlari
    if not change.is_new and onceki and onceki != g.sinav_notlari:
        satir += f"\n<i>(önceki: {html.escape(onceki)})</i>"
    satir += f"\nDurum: {durum}"
    return satir


def _format_baseline(grades: list[Grade]) -> str:
    lines = [
        "🤖 <b>FiratBot başladı!</b>",
        f"{len(grades)} ders takibe alındı. Yeni not girilince haber vereceğim.\n",
    ]
    for g in grades:
        lines.append(f"• <b>{html.escape(g.ders_adi)}</b>: {html.escape(g.sinav_notlari or '-')}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    notify = "--no-notify" not in argv

    config = Config.load()
    try:
        config.require_firat()
    except ConfigError as exc:
        print(f"[HATA] {exc}")
        return 1

    telegram_ok = bool(config.telegram_token and config.telegram_chat_id)
    if notify and not telegram_ok:
        print("[UYARI] Telegram ayarlanmamis; bildirim gonderilmeyecek.")

    print("Notlar cekiliyor...")
    try:
        grades = fetch_grades(config)
    except Exception as exc:  # noqa: BLE001 - tek pass; sonraki kosu tekrar dener
        print(f"[HATA] Not cekme basarisiz: {exc}")
        return 1
    print(f"  {len(grades)} ders bulundu.")

    old = state.load()
    if not old:
        print("Ilk calistirma: mevcut durum kaydediliyor (baseline).")
        if notify and telegram_ok:
            try:
                send(config, _format_baseline(grades))
            except Exception as exc:  # noqa: BLE001
                print(f"[UYARI] Baslangic mesaji gonderilemedi: {exc}")
        state.save(grades)
        return 0

    changes = _apply_filter(state.diff(old, grades), config.notify_filter)
    if not changes:
        print("Bildirilecek degisiklik yok.")
        state.save(grades)  # filtrelenen degisiklikleri de kaydet (tekrar tetiklenmesin)
        return 0

    print(f"  {len(changes)} degisiklik bildirilecek.")
    if notify and telegram_ok:
        message = "\n\n".join(_format_change(c) for c in changes)
        try:
            send(config, message)
            print("  Telegram bildirimi gonderildi.")
        except Exception as exc:  # noqa: BLE001 - state'i guncelleme, sonraki kosu tekrar denesin
            print(f"[HATA] Telegram gonderilemedi, state guncellenmiyor: {exc}")
            return 1
    else:
        for c in changes:
            print("  -", c.grade.ders_adi, c.grade.sinav_notlari)

    state.save(grades)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
