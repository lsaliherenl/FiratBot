# FiratBot — Fırat OBS Not Takip Botu

Fırat Üniversitesi OBS sistemine her **15 dakikada bir** otomatik girip **yeni/değişen not** olup olmadığını kontrol eden, değişiklik bulunca **Telegram'dan bildirim** gönderen bot.

## Nasıl çalışır?

1. OBS girişi CAS (SSO) + ASP.NET frame yapısı ve JS handoff kullandığı için gerçek tarayıcı (**Playwright/Chromium**) ile giriş yapılır.
2. Menüdeki **"Not Listesi"** sayfası (`not_listesi_op.aspx`) açılır, not tablosu (`#grd_not_listesi`) okunur.
3. Notlar `state.json`'daki önceki durumla karşılaştırılır; **yeni veya değişen** ders varsa Telegram'a mesaj gider.
4. `runner.py` sürekli çalışıp 15 dakikada bir bu kontrolü tekrarlar.

## ⚠️ Neden GitHub Actions değil de kendi PC?

OBS, **yurt dışı IP'lerden** gelen girişi (CAS ticket doğrulama aşamasında) reddediyor — GitHub Actions'ın ücretsiz sunucuları ABD/Avrupa'da olduğu için oradan giriş yapılamadı (`caserror.aspx`). Bu yüzden bot, **Türkiye IP'sine sahip kendi bilgisayarında** çalışır. PC açıkken kontrol eder; kapalıyken durur, açılınca kaldığı yerden devam eder.

> GitHub reposu (https://github.com/lsaliherenl/FiratBot) kod yedeği olarak durur; içindeki Actions workflow'u **devre dışı** bırakılmıştır.

## Dosyalar

| Dosya | Görev |
|------|-------|
| `runner.py` | Sürekli döngü: her 15 dk `check.py`'yi çalıştırır (PC'de bu çalışır) |
| `check.py` | Tek kontrol: giriş → not çek → diff → bildir → state güncelle |
| `firatbot/obs.py` | Playwright ile giriş + not tablosu parse (retry'li) |
| `firatbot/state.py` | `state.json` oku/yaz (gizlilik için **hash**), değişiklik hesapla |
| `firatbot/notifier.py` | Telegram mesajı gönder (retry'li) |
| `firatbot/config.py` | `.env` / ortam değişkenlerini oku |
| `debug_login.py` | Girişi test edip notları ekrana basar |
| `get_chat_id.py` | Telegram chat ID bulma yardımcısı |
| `run_check.bat` | Tek seferlik kontrolü elle çalıştırır (log: `run.log`) |
| `loop.log` | `runner.py` çalışma günlüğü |

## Kurulum (özet)

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

`.env` dosyası (`.env.example`'dan kopyala):

```
FIRAT_USERNAME=ogrenci_numaran
FIRAT_PASSWORD=obs_parolan
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Test:

```bash
python debug_login.py          # girişi + notları test et
python check.py --no-notify    # tam akış, mesaj göndermeden
```

## Otomatik çalıştırma (kurulu)

Bot, **oturum açılışında** otomatik başlar:
- Başlangıç klasöründe **`FiratBot.lnk`** kısayolu `pythonw runner.py`'yi penceresiz başlatır.
- `runner.py` arka planda sürekli çalışır, her 15 dk kontrol eder.

### Yönetim

- **Çalışıyor mu?** Görev Yöneticisi → `pythonw.exe` (veya `loop.log`'a bak).
- **Günlük:** `loop.log` (her kontrolün zamanı ve sonucu).
- **Durdur:** Görev Yöneticisi'nden `pythonw.exe`'yi sonlandır.
- **Yeniden başlat:** `pythonw "C:\AAA Projects\FiratBot\runner.py"` veya çıkış yapıp tekrar giriş.
- **Otomatik başlamayı kapat:** Başlangıç klasöründen `FiratBot.lnk`'yi sil
  (`shell:startup` → `Win+R` ile açılır).

## Güvenlik

- `.env` asla commit edilmez (`.gitignore`'da).
- `state.json` yalnızca **hash** içerir (okunabilir not/ders bilgisi sızmaz).
- Şifreler kodda değil; yerelde `.env`, GitHub'da (devre dışı workflow için) Secrets'ta.
