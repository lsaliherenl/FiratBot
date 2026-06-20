@echo off
rem FiratBot tek dosya .exe derleme (GUI + runner ayni exe).
rem Chromium gomulmez; calistirken %LOCALAPPDATA%\ms-playwright'taki tarayici kullanilir.
cd /d "%~dp0"
"C:\Python314\python.exe" -m PyInstaller --noconfirm --onefile --windowed ^
  --name FiratBot ^
  --collect-all playwright ^
  app.py
echo.
echo Bitti: dist\FiratBot.exe
