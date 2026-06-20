"""FiratBot ayar penceresi (Tkinter).

Tum ayarlari (OBS, Telegram, davranis) duzenler; botu baslatir/durdurur; giris ve
Telegram testleri yapar. Uzun isler (giris/test) arka plan thread'inde calisir.
"""
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

import requests

from . import paths, process, settings
from .config import Config
from .notifier import send
from .obs import fetch_grades

FILTER_LABELS = {"all": "Tüm değişiklikler", "final_only": "Sadece Final notları"}
FILTER_VALUES = {v: k for k, v in FILTER_LABELS.items()}


class FiratBotGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("FiratBot — Ayarlar")
        root.resizable(False, False)

        self.s = settings.load()
        self._build()
        self._load_into_fields()
        self._refresh_status()

    # ---------- arayuz ----------
    def _build(self) -> None:
        pad = {"padx": 8, "pady": 4}
        frm = ttk.Frame(self.root, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        # OBS
        obs = ttk.LabelFrame(frm, text="OBS Girişi", padding=8)
        obs.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(obs, text="Öğrenci No / Kullanıcı Adı").grid(row=0, column=0, sticky="w", **pad)
        self.e_user = ttk.Entry(obs, width=34)
        self.e_user.grid(row=0, column=1, **pad)
        ttk.Label(obs, text="Şifre").grid(row=1, column=0, sticky="w", **pad)
        self.e_pass = ttk.Entry(obs, width=34, show="●")
        self.e_pass.grid(row=1, column=1, **pad)
        self.show_pass = tk.BooleanVar(value=False)
        ttk.Checkbutton(obs, text="Göster", variable=self.show_pass,
                        command=self._toggle_pass).grid(row=1, column=2, **pad)

        # Telegram
        tg = ttk.LabelFrame(frm, text="Telegram", padding=8)
        tg.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(tg, text="Bot Token").grid(row=0, column=0, sticky="w", **pad)
        self.e_token = ttk.Entry(tg, width=34, show="●")
        self.e_token.grid(row=0, column=1, **pad)
        ttk.Label(tg, text="Chat ID").grid(row=1, column=0, sticky="w", **pad)
        self.e_chat = ttk.Entry(tg, width=34)
        self.e_chat.grid(row=1, column=1, **pad)
        ttk.Button(tg, text="Chat ID bul", command=self._find_chat_id).grid(row=1, column=2, **pad)

        # Davranis
        bh = ttk.LabelFrame(frm, text="Davranış", padding=8)
        bh.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(bh, text="Kontrol sıklığı (dk)").grid(row=0, column=0, sticky="w", **pad)
        self.e_interval = ttk.Spinbox(bh, from_=1, to=240, width=6)
        self.e_interval.grid(row=0, column=1, sticky="w", **pad)
        ttk.Label(bh, text="Bildirim").grid(row=1, column=0, sticky="w", **pad)
        self.cb_filter = ttk.Combobox(bh, values=list(FILTER_LABELS.values()),
                                      state="readonly", width=22)
        self.cb_filter.grid(row=1, column=1, sticky="w", **pad)
        self.autostart = tk.BooleanVar(value=True)
        ttk.Checkbutton(bh, text="Oturum açılışında otomatik başlat",
                        variable=self.autostart).grid(row=2, column=0, columnspan=2, sticky="w", **pad)

        # Aksiyon butonlari
        actions = ttk.Frame(frm)
        actions.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(actions, text="💾 Kaydet", command=self._save).grid(row=0, column=0, padx=4)
        ttk.Button(actions, text="Girişi test et", command=self._test_login).grid(row=0, column=1, padx=4)
        ttk.Button(actions, text="Telegram test", command=self._test_telegram).grid(row=0, column=2, padx=4)

        # Bot kontrol + durum
        ctl = ttk.LabelFrame(frm, text="Bot", padding=8)
        ctl.grid(row=4, column=0, sticky="ew")
        self.btn_start = ttk.Button(ctl, text="▶ Başlat", command=self._start_bot)
        self.btn_start.grid(row=0, column=0, padx=4, pady=4)
        self.btn_stop = ttk.Button(ctl, text="■ Durdur", command=self._stop_bot)
        self.btn_stop.grid(row=0, column=1, padx=4, pady=4)
        self.lbl_status = ttk.Label(ctl, text="●  durum", font=("Segoe UI", 10, "bold"))
        self.lbl_status.grid(row=0, column=2, padx=12, sticky="w")
        self.lbl_last = ttk.Label(ctl, text="")
        self.lbl_last.grid(row=1, column=0, columnspan=3, sticky="w", padx=4)

        self.log = tk.Text(ctl, height=7, width=60, state="disabled", font=("Consolas", 9),
                           background="#111", foreground="#ccc")
        self.log.grid(row=2, column=0, columnspan=3, pady=(6, 0))

        # Alt mesaj
        self.msg = ttk.Label(frm, text="", foreground="#444")
        self.msg.grid(row=5, column=0, sticky="w", pady=(8, 0))

    def _toggle_pass(self) -> None:
        self.e_pass.config(show="" if self.show_pass.get() else "●")

    def _load_into_fields(self) -> None:
        self._set(self.e_user, self.s.firat_username)
        self._set(self.e_pass, self.s.firat_password)
        self._set(self.e_token, self.s.telegram_token)
        self._set(self.e_chat, self.s.telegram_chat_id)
        self._set(self.e_interval, str(self.s.interval_minutes))
        self.cb_filter.set(FILTER_LABELS.get(self.s.notify_filter, FILTER_LABELS["all"]))
        self.autostart.set(self.s.autostart)

    @staticmethod
    def _set(entry, value) -> None:
        entry.delete(0, tk.END)
        entry.insert(0, value or "")

    # ---------- ayarlar ----------
    def _collect(self) -> settings.Settings:
        try:
            interval = max(1, int(self.e_interval.get()))
        except ValueError:
            interval = 15
        return settings.Settings(
            firat_username=self.e_user.get().strip(),
            firat_password=self.e_pass.get(),
            telegram_token=self.e_token.get().strip(),
            telegram_chat_id=self.e_chat.get().strip(),
            interval_minutes=interval,
            notify_filter=FILTER_VALUES.get(self.cb_filter.get(), "all"),
            autostart=self.autostart.get(),
        )

    def _save(self) -> None:
        self.s = self._collect()
        settings.save(self.s)
        try:
            process.set_autostart(self.s.autostart)
        except Exception as exc:  # noqa: BLE001
            self._flash(f"Ayarlar kaydedildi ama otomatik başlat ayarlanamadı: {exc}", err=True)
            return
        self._flash("Ayarlar kaydedildi. ✅")

    def _config_from_fields(self) -> Config:
        s = self._collect()
        return Config(s.firat_username, s.firat_password, s.telegram_token,
                      s.telegram_chat_id, s.interval_minutes, s.notify_filter)

    # ---------- testler (thread'li) ----------
    def _run_bg(self, fn, on_done) -> None:
        def worker():
            try:
                result = fn()
                self.root.after(0, lambda: on_done(True, result))
            except Exception as exc:  # noqa: BLE001
                self.root.after(0, lambda: on_done(False, exc))
        threading.Thread(target=worker, daemon=True).start()

    def _test_login(self) -> None:
        cfg = self._config_from_fields()
        if not cfg.firat_username or not cfg.firat_password:
            self._flash("Önce kullanıcı adı ve şifreyi girin.", err=True)
            return
        self._flash("Giriş test ediliyor... (birkaç saniye)")
        self._run_bg(lambda: fetch_grades(cfg), self._login_done)

    def _login_done(self, ok, result) -> None:
        if ok:
            self._flash(f"✅ Giriş başarılı — {len(result)} ders bulundu.")
        else:
            self._flash(f"❌ Giriş başarısız: {result}", err=True)

    def _test_telegram(self) -> None:
        cfg = self._config_from_fields()
        if not cfg.telegram_token or not cfg.telegram_chat_id:
            self._flash("Önce Telegram token ve chat ID girin.", err=True)
            return
        self._flash("Telegram test mesajı gönderiliyor...")
        self._run_bg(
            lambda: send(cfg, "✅ <b>FiratBot</b> test mesajı — bağlantı çalışıyor!"),
            lambda ok, r: self._flash("✅ Test mesajı gönderildi." if ok else f"❌ Gönderilemedi: {r}", err=not ok),
        )

    def _find_chat_id(self) -> None:
        token = self.e_token.get().strip()
        if not token:
            self._flash("Önce Telegram token girin.", err=True)
            return
        self._flash("Chat ID aranıyor... (önce bota /start yazın)")

        def fetch():
            r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20)
            data = r.json()
            if not data.get("ok"):
                raise RuntimeError(str(data))
            for upd in reversed(data.get("result", [])):
                msg = upd.get("message") or upd.get("edited_message") or {}
                chat = msg.get("chat") or {}
                if chat.get("id") is not None:
                    return str(chat["id"])
            raise RuntimeError("Mesaj bulunamadı. Bota bir mesaj atıp tekrar deneyin.")

        def done(ok, result):
            if ok:
                self._set(self.e_chat, result)
                self._flash(f"✅ Chat ID bulundu: {result}")
            else:
                self._flash(f"❌ {result}", err=True)

        self._run_bg(fetch, done)

    # ---------- bot kontrol ----------
    def _start_bot(self) -> None:
        # Once mevcut alanlari kaydet ki runner guncel ayarlarla calissin
        self._save()
        started = process.start()
        self._flash("Bot başlatıldı." if started else "Bot zaten çalışıyor.")
        self._refresh_status()

    def _stop_bot(self) -> None:
        stopped = process.stop()
        self._flash("Bot durduruldu." if stopped else "Bot zaten durmuş.")
        self._refresh_status()

    def _refresh_status(self) -> None:
        running = process.is_running()
        st = process.read_status()
        if running:
            self.lbl_status.config(text=f"●  Çalışıyor (PID {st.get('pid','?')})", foreground="#1a7f37")
        else:
            self.lbl_status.config(text="●  Durdu", foreground="#b00")
        last = st.get("last_run")
        res = st.get("last_result")
        self.lbl_last.config(text=f"Son kontrol: {last} — {res}" if last else "Henüz kontrol yapılmadı.")
        self._load_log_tail()
        self.root.after(2000, self._refresh_status)

    def _load_log_tail(self, lines: int = 12) -> None:
        try:
            text = paths.LOG_FILE.read_text(encoding="utf-8", errors="replace")
            tail = "\n".join(text.splitlines()[-lines:])
        except OSError:
            tail = "(log yok)"
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log.insert(tk.END, tail)
        self.log.see(tk.END)
        self.log.config(state="disabled")

    # ---------- yardimci ----------
    def _flash(self, text: str, err: bool = False) -> None:
        self.msg.config(text=text, foreground="#b00" if err else "#1a7f37")


def main() -> None:
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass
    FiratBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
