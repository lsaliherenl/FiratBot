"""FiratBot ana akis: giris -> notlari cek -> degisiklikleri bul -> Telegram'a bildir -> state guncelle.

Tek seferlik calisir ve cikar. Zamanlamayi GitHub Actions (cron) yapar.

Kullanim:
    python check.py            # normal calistirma
    python check.py --no-notify  # bildirim gondermeden (yerel test)
"""
from __future__ import annotations

import html
import sys

from firatbot import state
from firatbot.config import Config, ConfigError
from firatbot.notifier import send
from firatbot.obs import Grade, fetch_grades


def _format_change(change: state.Change) -> str:
    g = change.grade
    ders = html.escape(f"{g.ders_kodu} — {g.ders_adi}")
    notlar = html.escape(g.sinav_notlari or "-")
    durum = html.escape(g.durum or "-")
    baslik = "🆕 Yeni ders/not" if change.is_new else "📢 Not güncellendi"
    return f"<b>{baslik}</b>\n📚 {ders}\n📝 {notlar}\nDurum: {durum}"


def _format_baseline(grades: list[Grade]) -> str:
    lines = ["🤖 <b>FiratBot başladı!</b>", f"{len(grades)} ders takibe alındı. Yeni not girilince haber vereceğim.\n"]
    for g in grades:
        lines.append(f"• <b>{html.escape(g.ders_adi)}</b>: {html.escape(g.sinav_notlari or '-')}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    notify = "--no-notify" not in argv

    try:
        config = Config.load() if notify else Config.load_firat_only()
    except ConfigError as exc:
        print(f"[HATA] Yapilandirma: {exc}")
        return 1

    print("Notlar cekiliyor...")
    try:
        grades = fetch_grades(config)
    except Exception as exc:  # noqa: BLE001 - tek pass; bir sonraki kosu tekrar dener
        print(f"[HATA] Not cekme basarisiz: {exc}")
        return 1
    print(f"  {len(grades)} ders bulundu.")

    old = state.load()
    is_first_run = not old

    if is_first_run:
        # Ilk kosu: mevcut notlari baz al, her ders icin spam yapma.
        print("Ilk calistirma: mevcut durum kaydediliyor (baseline).")
        if notify:
            try:
                send(config, _format_baseline(grades))
            except Exception as exc:  # noqa: BLE001
                print(f"[UYARI] Baslangic mesaji gonderilemedi: {exc}")
        state.save(grades)
        return 0

    changes = state.diff(old, grades)
    if not changes:
        print("Degisiklik yok.")
        return 0

    print(f"  {len(changes)} degisiklik bulundu.")
    if notify:
        message = "\n\n".join(_format_change(c) for c in changes)
        try:
            send(config, message)
            print("  Telegram bildirimi gonderildi.")
        except Exception as exc:  # noqa: BLE001 - state'i guncelleme, sonraki kosu tekrar denesin
            print(f"[HATA] Telegram gonderilemedi, state guncellenmiyor: {exc}")
            return 1
    else:
        for c in changes:
            print("  -", c.grade.ders_kodu, c.grade.sinav_notlari)

    state.save(grades)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
