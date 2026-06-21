@echo off
rem FiratBot tek-klasor (onedir) derleme (GUI + runner ayni exe).
rem onedir secildi: onefile, her calismada _MEI gecici klasorune acilir ve
rem Playwright alt-surecleri dosyalari kilitledigi icin kapanista "Failed to
rem remove temporary directory" uyarisi verir. onedir'de bu sorun yok + daha hizli.
rem Chromium gomulmez; calistirken %LOCALAPPDATA%\ms-playwright'taki tarayici kullanilir.
cd /d "%~dp0"
"C:\Python314\python.exe" -m PyInstaller --noconfirm --onedir --windowed ^
  --name FiratBot ^
  --collect-all playwright ^
  app.py
echo.
echo Bitti: dist\FiratBot\FiratBot.exe
