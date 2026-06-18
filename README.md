# FiratBot — Fırat OBS Not Takip Botu

Fırat Üniversitesi OBS sistemine düzenli aralıklarla otomatik girip **yeni not girilmiş mi** diye kontrol eden, yeni/değişen not bulunca **Telegram'dan bildirim** gönderen bot.

## Nasıl çalışır?

1. OBS girişi CAS (SSO) + ASP.NET frame yapısı ve JS handoff kullandığı için gerçek tarayıcı (**Playwright/Chromium**) ile giriş yapılır.
2. Menüdeki **"Not Listesi"** sayfası (`not_listesi_op.aspx`) açılır, not tablosu (`#grd_not_listesi`) okunur.
3. Çekilen notlar `state.json`'daki önceki durumla karşılaştırılır; **yeni veya değişen** ders varsa Telegram'a mesaj gider.
4. Zamanlamayı **GitHub Actions** (cron `*/15`) yapar; her koşu tek seferlik çalışır.

## Dosyalar

| Dosya | Görev |
|------|-------|
| `check.py` | Ana akış: giriş → not çek → diff → bildir → state güncelle |
| `firatbot/obs.py` | Playwright ile giriş + not tablosu parse |
| `firatbot/state.py` | `state.json` oku/yaz, değişiklik hesapla |
| `firatbot/notifier.py` | Telegram mesajı gönder |
| `firatbot/config.py` | `.env` / ortam değişkenlerini oku |
| `debug_login.py` | Girişi test edip notları ekrana basar (Telegram gerektirmez) |
| `get_chat_id.py` | Telegram chat ID bulma yardımcısı |
| `.github/workflows/check.yml` | 7/24 zamanlanmış çalıştırma |

## Yerel kurulum

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

`.env` dosyası oluştur (`.env.example`'ı kopyala) ve doldur:

```
FIRAT_USERNAME=ogrenci_numaran
FIRAT_PASSWORD=obs_parolan
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Girişi ve not çekmeyi test et (Telegram gerekmez):

```bash
python debug_login.py          # notları ekrana basar
python check.py --no-notify    # tam akış, mesaj göndermeden
```

## Telegram kurulumu

1. Telegram'da **@BotFather** → `/newbot` → bota isim ver → çıkan **token**'i `.env` → `TELEGRAM_TOKEN`'a yaz.
2. Oluşturduğun botu aç ve ona bir mesaj at (örn. `/start`).
3. `python get_chat_id.py` çalıştır → çıkan **chat_id**'yi `.env` → `TELEGRAM_CHAT_ID`'ye yaz.

## GitHub Actions ile 7/24 çalıştırma

1. Projeyi **private** bir GitHub reposuna gönder (güvenlik için private şart).
2. Repo → **Settings → Secrets and variables → Actions → New repository secret** ile şu 4 secret'ı ekle:
   `FIRAT_USERNAME`, `FIRAT_PASSWORD`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`.
3. **Actions** sekmesinden workflow'u etkinleştir; `Not Kontrol → Run workflow` ile elle test et.
4. Sonra `cron` her ~15 dakikada otomatik çalışır. İlk koşu mevcut notları "baz" alıp bir başlangıç mesajı atar; sonrakiler sadece **yeni/değişen** notları bildirir.

> Not: `state.json` her koşuda repoya commit'lenerek durum korunur. Parolalar yalnızca GitHub Secrets'ta tutulur, koda yazılmaz.

## Güvenlik

- `.env` asla commit edilmez (`.gitignore`'da).
- Repo **private** olmalı; `state.json` ders/not bilgini içerir.
- Bilgiler kodda değil, ortam değişkeni / GitHub Secrets'tadır.
