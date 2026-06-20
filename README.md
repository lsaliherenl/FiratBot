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

## Ayar arayüzü (GUI)

Tüm ayarlar artık koddan değil **arayüzden** yönetilir. Masaüstündeki **"FiratBot Ayarlar"** kısayolu (`FiratBot.exe`) ile açılır:

- **OBS** (kullanıcı adı/şifre) ve **Telegram** (token/chat ID) alanları
- **Girişi test et**, **Telegram test**, **Chat ID bul** butonları
- **Davranış:** kontrol sıklığı (dk), bildirim filtresi (Tüm değişiklikler / Sadece Final), oturum açılışında otomatik başlat
- **Botu Başlat/Durdur** + canlı durum (çalışıyor mu, son kontrol, son loglar)

Tek bir `FiratBot.exe` iki modda çalışır: argümansız → **GUI**, `--run` → **arka plan botu**.

Ayarlar/loglar `%APPDATA%\FiratBot\` altında tutulur (`settings.json`, `state.json`, `loop.log`, `status.json`). Şifre ve token **Windows DPAPI** ile şifrelenir; dosyada düz metin parola bulunmaz.

## Dosyalar

| Dosya | Görev |
|------|-------|
| `app.py` | Giriş noktası: argümansız → GUI, `--run` → bot döngüsü (PyInstaller bunu derler) |
| `firatbot/gui.py` | Tkinter ayar penceresi |
| `firatbot/settings.py` | `settings.json` oku/yaz; sırları DPAPI ile şifreler |
| `firatbot/secretstore.py` | Windows DPAPI şifrele/çöz (bağımlılıksız) |
| `firatbot/process.py` | Botu başlat/durdur/durum + Startup kısayolu |
| `firatbot/paths.py` | `%APPDATA%\FiratBot` yolları |
| `firatbot/runner.py` | Sürekli döngü (her N dk `check.py`) |
| `check.py` | Tek kontrol: giriş → not çek → diff → filtre → bildir → state |
| `firatbot/obs.py` | Playwright ile giriş + not tablosu parse (retry'li) |
| `firatbot/state.py` | `state.json` oku/yaz, değişiklik hesapla |
| `firatbot/notifier.py` | Telegram mesajı gönder (retry'li) |
| `firatbot/config.py` | `settings.json`'dan yapılandırma (.env fallback) |
| `build.bat` | PyInstaller ile `dist\FiratBot.exe` üretir |
| `debug_login.py` / `get_chat_id.py` | Yardımcı/test scriptleri |

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

## Exe derleme

```bash
build.bat        # -> dist\FiratBot.exe
```
Chromium exe'ye gömülmez; çalışırken `%LOCALAPPDATA%\ms-playwright`'taki kurulu tarayıcı kullanılır (önce `python -m playwright install chromium`).

## Otomatik çalıştırma (kurulu)

- **Bot:** Başlangıç klasöründeki `FiratBot.lnk` → `FiratBot.exe --run` penceresiz başlar, her N dk kontrol eder.
- **Ayarlar:** Masaüstündeki `FiratBot Ayarlar` → `FiratBot.exe` (GUI).
- GUI'deki **Başlat/Durdur** ve **otomatik başlat** kutusu bu kısayolları/süreci yönetir.

### Yönetim
- **Çalışıyor mu / son kontrol:** GUI'deki durum panelinde; ya da `%APPDATA%\FiratBot\status.json` / `loop.log`.
- **Durdur/Başlat:** GUI'den; ya da Görev Yöneticisi'nden `FiratBot.exe`.
- **Otomatik başlamayı kapat:** GUI'de kutuyu kaldır (Startup kısayolunu siler).

## Güvenlik

- `.env` / `settings.json` commit edilmez (`.gitignore`'da).
- Şifre ve Telegram token **Windows DPAPI** ile şifreli (`settings.json`'da düz metin parola yok); yalnız o Windows kullanıcısı çözebilir.
- Notlar `%APPDATA%\FiratBot\state.json`'da yerelde tutulur (repoya gitmez).
