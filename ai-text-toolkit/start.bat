@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 is not installed. Install it from https://www.python.org/downloads/
  echo IMPORTANT: check "Add Python to PATH" during install, then run this file again.
  pause
  exit /b 1
)
if not exist .venv (
  echo First run: setting things up, this takes a minute...
  python -m venv .venv
  .venv\Scripts\pip install -q -r requirements.txt
)
echo.
echo ============================================
echo   Textuvia starting...
echo   Your browser will open automatically.
echo   Keep this window open while using the app.
echo   Close this window to stop the app.
echo ============================================
echo.
start "" /min cmd /c "timeout /t 3 /nobreak >nul & start "" http://127.0.0.1:8000"
.venv\Scripts\python run.py
pause
