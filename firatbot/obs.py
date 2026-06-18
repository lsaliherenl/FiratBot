"""Firat OBS'ye girip not listesini ceken modul (Playwright tabanli).

OBS, CAS (SSO) + ASP.NET frame yapisi ve JS handoff (gkm) kullaniyor; bu yuzden
saf requests yerine gercek tarayici (Playwright/Chromium) kullaniyoruz.

Akis:
  1. login.aspx -> CAS login formu doldur -> index.aspx (menu) yuklenir.
  2. Menudeki "Not Listesi" ogesinin onclick'inden gkm URL'i cikarilir.
  3. myOnFrameClick(url) cagrilarak not sayfasi icerik frame'ine yuklenir.
  4. not_listesi_op.aspx frame'indeki tablo (#grd_not_listesi) parse edilir.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from bs4 import BeautifulSoup
from playwright.sync_api import Frame, sync_playwright

from .config import Config

LOGIN_URL = "https://obs.firat.edu.tr/oibs/std/login.aspx"
GRADES_FRAME_HINT = "not_listesi_op.aspx"
GRADES_TABLE_ID = "grd_not_listesi"


class ScrapeError(RuntimeError):
    """Not listesi cekilemedi."""


@dataclass(frozen=True)
class Grade:
    ders_kodu: str
    ders_adi: str
    sinav_notlari: str
    ortalama: str
    harf_notu: str
    durum: str

    @property
    def key(self) -> str:
        return self.ders_kodu

    @property
    def value(self) -> str:
        """Yeni not tespitinde kiyaslanan, degisince haber verilecek alanlar."""
        return f"{self.sinav_notlari} | ort={self.ortalama} | not={self.harf_notu} | {self.durum}"

    def as_dict(self) -> dict:
        return asdict(self)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def _parse_grades(html: str) -> list[Grade]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id=GRADES_TABLE_ID)
    if table is None:
        raise ScrapeError(
            f"Not tablosu (#{GRADES_TABLE_ID}) bulunamadi; sayfa yapisi degismis olabilir."
        )

    grades: list[Grade] = []
    rows = table.find_all("tr")
    for row in rows[1:]:  # ilk satir baslik
        cells = [_clean(c.get_text(" ", strip=True)) for c in row.find_all(["td", "th"])]
        if len(cells) < 8:
            continue
        # Sutunlar: Sb | Ders Kodu | Ders Adi | Sonuc.Durumu | Sinav Notlari | Ort | Not | Durumu | (Istatistik)
        ders_kodu = cells[1]
        if not ders_kodu:
            continue
        grades.append(
            Grade(
                ders_kodu=ders_kodu,
                ders_adi=cells[2],
                sinav_notlari=cells[4],
                ortalama=cells[5],
                harf_notu=cells[6],
                durum=cells[7],
            )
        )
    return grades


def _find_grades_frame(page) -> Frame | None:
    for fr in page.frames:
        if GRADES_FRAME_HINT in fr.url:
            return fr
    return None


def fetch_grades(config: Config, headless: bool = True, timeout_ms: int = 45000) -> list[Grade]:
    """OBS'ye girip not listesini ceker ve Grade listesi dondurur."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        try:
            page = browser.new_context().new_page()
            page.set_default_timeout(timeout_ms)

            # 1) Giris (CAS login formu)
            page.goto(LOGIN_URL, wait_until="domcontentloaded")
            page.wait_for_selector("#username")
            page.fill("#username", config.firat_username)
            page.fill("#password", config.firat_password)
            # Formu dogrudan submit et (Enter, login formunu tetikler; belirsiz buton secimi yerine)
            page.press("#password", "Enter")
            try:
                page.wait_for_url(lambda u: "obs.firat.edu.tr/oibs/std/index.aspx" in u)
            except Exception:
                pass  # asagida net tani veriyoruz
            page.wait_for_load_state("networkidle")

            if "index.aspx" not in page.url:
                # Tani: CAS hata mesaji var mi yoksa baska sayfa mi
                detail = ""
                try:
                    err = page.query_selector(".errors, .alert-danger, #status, #msg")
                    if err:
                        detail = _clean(err.inner_text())[:200]
                    if not detail:
                        detail = _clean(page.inner_text("body"))[:200]
                except Exception:
                    pass
                raise ScrapeError(
                    f"Giris sonrasi beklenen sayfaya ulasilamadi (URL: {page.url}). "
                    f"Sayfa ozeti: {detail!r}"
                )

            # 2) "Not Listesi" menu ogesinin hedef URL'ini bul
            onclick = page.evaluate(
                """() => {
                    let r = null;
                    document.querySelectorAll('[onclick]').forEach(e => {
                        if ((e.innerText || '').trim() === 'Not Listesi') r = e.getAttribute('onclick');
                    });
                    return r;
                }"""
            )
            if not onclick:
                raise ScrapeError("'Not Listesi' menu ogesi bulunamadi.")
            match = re.search(r"menu_close\(this,'([^']+)'\)", onclick)
            if not match:
                raise ScrapeError("'Not Listesi' baglantisi cozumlenemedi.")
            target_url = match.group(1)

            # 3) Sayfayi icerik frame'ine yukle (top-level goto session'i bozuyor)
            page.evaluate("(u) => myOnFrameClick(u)", target_url)

            # 4) Not frame'i yuklenene kadar bekle ve HTML'i al
            page.wait_for_function(
                """(hint) => Array.from(document.querySelectorAll('iframe, frame'))
                    .some(f => (f.contentWindow && f.contentWindow.location.href || '').includes(hint))""",
                arg=GRADES_FRAME_HINT,
            )
            frame = _find_grades_frame(page)
            if frame is None:
                raise ScrapeError("Not listesi frame'i yuklenemedi.")
            frame.wait_for_selector(f"#{GRADES_TABLE_ID}", timeout=timeout_ms)
            html = frame.content()
            return _parse_grades(html)
        finally:
            browser.close()
