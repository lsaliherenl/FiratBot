@echo off
rem FiratBot - tek kontrol calistirir, ciktisini run.log'a yazar.
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
rem Tarayici yolunu sabitle (Gorev Zamanlayici kisitli ortamda LOCALAPPDATA cozemeyebiliyor)
set PLAYWRIGHT_BROWSERS_PATH=C:\Users\90555\AppData\Local\ms-playwright
cd /d "%~dp0"
echo --- %date% %time% --- >> "%~dp0run.log"
echo [env] LOCALAPPDATA=%LOCALAPPDATA% USERPROFILE=%USERPROFILE% >> "%~dp0run.log"
"C:\Python314\python.exe" check.py >> "%~dp0run.log" 2>&1
